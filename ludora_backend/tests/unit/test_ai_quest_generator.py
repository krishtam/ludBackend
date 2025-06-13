import pytest
from unittest.mock import patch, AsyncMock, MagicMock # Added AsyncMock for async functions

from ludora_backend.app.models.user import User
from ludora_backend.app.models.quest import Quest, QuestObjective
from ludora_backend.app.models.enums import QuestStatus, QuestObjectiveType
from ludora_backend.app.schemas.ai_models import PredictedWeakness, WeaknessPredictionOutput
from ludora_backend.app.services.quest_generator_service import generate_quests_for_user, _apply_quest_generation_rules
# Import session from weakness_predictor to mock its state
from ludora_backend.app.services.ai_models import weakness_predictor

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
async def mock_user(): # No need for db_setup_module if we mock all DB calls
    # Create a mock User object, not necessarily a DB instance for these unit tests
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "unit_test_user"
    return user

@pytest.fixture
def dummy_weaknesses_high_level():
    return [
        PredictedWeakness(topic_id="Topic_Algebra", weakness_probability=0.8, suggested_action_level=2),
        PredictedWeakness(topic_id="Topic_Geometry", weakness_probability=0.75, suggested_action_level=3),
    ]

@pytest.fixture
def dummy_weaknesses_low_level():
    return [
        PredictedWeakness(topic_id="Topic_Calculus", weakness_probability=0.4, suggested_action_level=1),
    ]

async def test_apply_quest_generation_rules_high_level_weakness(dummy_weaknesses_high_level, mock_user):
    """Test rule engine with high suggested action levels."""
    # No need to mock Topic.get_or_none if we pass string topic_ids directly
    # and the rule engine formats names based on these strings.
    # If it did DB lookups, we'd mock Topic.get_or_none.

    result_quest_data = await _apply_quest_generation_rules(mock_user, dummy_weaknesses_high_level)

    assert len(result_quest_data) == 2 # Should generate quests for both high-level weaknesses

    quest1_data = result_quest_data[0]
    assert "Strengthen Your Skills: Topic Algebra" in quest1_data["name"]
    assert len(quest1_data["objectives"]) >= 1 # At least one objective for answering questions
    assert quest1_data["objectives"][0].objective_type == QuestObjectiveType.ANSWER_QUESTIONS_ON_TOPIC
    assert quest1_data["objectives"][0].target_id == "Topic_Algebra"
    assert quest1_data["objectives"][0].target_count == 5

    quest2_data = result_quest_data[1]
    assert "Strengthen Your Skills: Topic Geometry" in quest2_data["name"]
    assert len(quest2_data["objectives"]) >= 1
    assert quest2_data["objectives"][0].objective_type == QuestObjectiveType.ANSWER_QUESTIONS_ON_TOPIC
    assert quest2_data["objectives"][0].target_id == "Topic_Geometry"

async def test_apply_quest_generation_rules_low_level_weakness(dummy_weaknesses_low_level, mock_user):
    """Test rule engine with low suggested action levels (should generate no quests)."""
    result_quest_data = await _apply_quest_generation_rules(mock_user, dummy_weaknesses_low_level)
    assert len(result_quest_data) == 0

@patch('ludora_backend.app.services.quest_generator_service.QuestObjective.create', new_callable=AsyncMock)
@patch('ludora_backend.app.services.quest_generator_service.Quest.create', new_callable=AsyncMock)
@patch('ludora_backend.app.services.quest_generator_service.Quest.filter') # To mock existing_quest check
async def test_generate_quests_for_user_creates_quests(
    mock_quest_filter: MagicMock,
    mock_quest_create: AsyncMock,
    mock_objective_create: AsyncMock,
    mock_user: User,
    dummy_weaknesses_high_level: List[PredictedWeakness]
):
    """Test the main service function creates quests and objectives based on rules."""

    # Mock Quest.filter(...).first() to return None (no existing active quests with same name)
    mock_quest_filter.return_value.first = AsyncMock(return_value=None)

    # Mock the return value of Quest.create
    # It needs to be an object that can have 'fetch_related' called on it.
    mock_db_quest_instance = MagicMock(spec=Quest)
    mock_db_quest_instance.name = "Generated Quest Name" # Set some attributes for print statements
    mock_db_quest_instance.fetch_related = AsyncMock() # Mock fetch_related
    mock_quest_create.return_value = mock_db_quest_instance

    # Mock the weakness predictor session to be None, so dummy data is used
    with patch.object(weakness_predictor, 'session', None):
        # The service function _apply_quest_generation_rules is called internally.
        # We are effectively testing its output combined with DB interaction mocks.
        # To make this test more focused on generate_quests_for_user's DB logic,
        # we could also patch _apply_quest_generation_rules itself.
        # For now, let its placeholder logic run with dummy_weaknesses_high_level
        # (which are forced by wp_session being None).

        # Override the dummy weaknesses used in the service when wp_session is None
        # by patching the list directly if needed, or ensure the default dummy is suitable.
        # The service already uses a fixed dummy list if wp_session is None.
        # Let's ensure those fixed dummy weaknesses are the ones we expect for this test.
        # The service's default dummy weaknesses are:
        # PredictedWeakness(topic_id="Basic Operations", weakness_probability=0.8, suggested_action_level=2)
        # PredictedWeakness(topic_id="Fractions and Decimals", weakness_probability=0.7, suggested_action_level=1) -> this one won't create a quest

        # So, we expect one quest for "Basic Operations".

        created_quests = await generate_quests_for_user(mock_user)

    assert len(created_quests) == 1 # Based on the service's internal dummy data when wp_session is None
    mock_quest_create.assert_called_once() # Should be called once for "Basic Operations"

    # Objectives for "Basic Operations" quest (currently 1 in placeholder rule engine)
    assert mock_objective_create.call_count >= 1

    # Verify attributes of the first (and only) quest created
    call_args_quest = mock_quest_create.call_args[1] # kwargs
    assert call_args_quest['user'] == mock_user
    assert "Basic Operations" in call_args_quest['name']
    assert call_args_quest['status'] == QuestStatus.ACTIVE

    # Verify attributes of the first objective created
    call_args_obj = mock_objective_create.call_args_list[0][1] # kwargs of first call
    assert call_args_obj['quest'] == mock_db_quest_instance
    assert call_args_obj['objective_type'] == QuestObjectiveType.ANSWER_QUESTIONS_ON_TOPIC
    assert call_args_obj['target_id'] == "Basic Operations" # From the dummy weakness data in service

    mock_db_quest_instance.fetch_related.assert_called_with('objectives')


@patch('ludora_backend.app.services.quest_generator_service.Quest.filter')
async def test_generate_quests_for_user_skips_existing_active_quest(
    mock_quest_filter: MagicMock,
    mock_user: User
):
    """Test that new quests are not generated if an identical active one exists."""

    # Simulate that a quest with the generated name already exists and is active
    mock_quest_filter.return_value.first = AsyncMock(return_value=MagicMock(spec=Quest)) # Returns a mock Quest

    with patch.object(weakness_predictor, 'session', None): # Use dummy weaknesses
        created_quests = await generate_quests_for_user(mock_user)

    assert len(created_quests) == 0 # No new quests should be created

async def test_generate_quests_for_user_no_actionable_weaknesses(mock_user: User, dummy_weaknesses_low_level: List[PredictedWeakness]):
    """Test quest generation when weaknesses do not meet criteria for quest creation."""

    # Patch _apply_quest_generation_rules to return no quest data
    # based on low_level weaknesses (which it should do by its logic).
    # Or, more directly, patch the dummy list in the service if wp_session is None

    # For this test, let's assume the internal dummy data when wp_session is None
    # might still produce some quests. We need to ensure the _apply_quest_generation_rules
    # part is tested. We can do this by providing different dummy weaknesses.
    # The service's current behavior is to use its own fixed dummy list when wp_session is None.
    # To test this specific scenario, we should mock what _apply_quest_generation_rules returns.

    with patch('ludora_backend.app.services.quest_generator_service._apply_quest_generation_rules', AsyncMock(return_value=[])):
        with patch.object(weakness_predictor, 'session', MagicMock()): # Simulate wp_session is active to use patched _apply_quest_generation_rules
             # This is a bit convoluted. The service has two paths for user_weaknesses:
             # 1. wp_session is None -> uses hardcoded dummy weaknesses.
             # 2. wp_session is not None -> would call predict_user_weakness (which we'd mock for unit test)
             # Let's simplify: Assume _apply_quest_generation_rules is the core logic to test here.
             # We've tested _apply_quest_generation_rules separately.
             # This test for generate_quests_for_user should focus on its orchestration.

             # Re-think: We want to test generate_quests_for_user when _apply_quest_generation_rules returns empty.
             # The easiest way is to ensure the dummy weaknesses used lead to empty rules output.
             # The default dummy list in generate_quests_for_user has one actionable weakness.
             # Let's patch the dummy list used inside generate_quests_for_user when wp_session is None.

             # This is still tricky because that list is local to the function scope if wp_session is None.
             # Alternative: Patch _apply_quest_generation_rules directly.

            created_quests = await generate_quests_for_user(mock_user) # This will use the patched _apply_...
            assert len(created_quests) == 0
            print(f"Test with no actionable weaknesses, created quests: {len(created_quests)}")
