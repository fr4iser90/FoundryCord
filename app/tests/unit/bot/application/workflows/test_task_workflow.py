import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio

from app.bot.application.workflows.task_workflow import TaskWorkflow, WorkflowStatus # Assuming WorkflowStatus might be used later
from app.bot.application.workflows.database_workflow import DatabaseWorkflow
import nextcord

# --- Fixtures ---

@pytest.fixture
def mock_db_workflow():
    return MagicMock(spec=DatabaseWorkflow)

@pytest.fixture
def mock_bot():
    # Basic bot mock, can be expanded if needed for specific task interactions
    bot = AsyncMock(name="MockBot")
    return bot

@pytest.fixture
def task_workflow_instance(mock_db_workflow, mock_bot):
    return TaskWorkflow(database_workflow=mock_db_workflow, bot=mock_bot)

# Async helper for side_effect to raise CancelledError
async def async_raiser_cancelled_error_side_effect(*args, **kwargs):
    raise asyncio.CancelledError("Simulated task cancellation by async_raiser")

# --- Test Initialize ---

@pytest.mark.asyncio
async def test_initialize_success(task_workflow_instance, mocker):
    """Test successful global initialization of the task workflow."""
    mock_register_tasks = mocker.patch.object(task_workflow_instance, 'register_background_tasks')
    
    result = await task_workflow_instance.initialize()
    
    assert result is True
    assert task_workflow_instance.running is True
    mock_register_tasks.assert_called_once()
    # Check dependencies (inherited from BaseWorkflow)
    assert "database" in task_workflow_instance.get_dependencies()
    assert task_workflow_instance.requires_guild_approval is True


@pytest.mark.asyncio
async def test_initialize_handles_exception_during_registration(task_workflow_instance, mocker):
    """Test initialize handles errors during task registration and returns False."""
    mock_logger_error = mocker.patch("app.bot.application.workflows.task_workflow.logger.error")
    mocker.patch.object(task_workflow_instance, 'register_background_tasks', side_effect=Exception("Registration Failed!"))
    
    result = await task_workflow_instance.initialize()
    
    assert result is False
    assert task_workflow_instance.running is False # Should remain false or be reset
    mock_logger_error.assert_any_call("Error initializing task workflow: Registration Failed!")


# --- Test Cleanup ---

@pytest.mark.asyncio
async def test_cleanup_cancels_and_clears_tasks(task_workflow_instance, mocker):
    """Test cleanup cancels running tasks and clears the task list."""
    mock_task1 = AsyncMock(spec=asyncio.Task) 
    mock_task1.done.return_value = False
    mock_task1.side_effect = async_raiser_cancelled_error_side_effect # Use async helper
    # Ensure cancel is a mock we can assert on the AsyncMock itself
    mock_task1.cancel = MagicMock(name="cancel_mock_task1") 

    mock_task2 = AsyncMock(spec=asyncio.Task)
    mock_task2.done.return_value = False
    mock_task2.side_effect = async_raiser_cancelled_error_side_effect # Use async helper
    mock_task2.cancel = MagicMock(name="cancel_mock_task2")
    
    task_workflow_instance.tasks = [mock_task1, mock_task2]
    task_workflow_instance.running = True
    
    await task_workflow_instance.cleanup()
    
    assert task_workflow_instance.running is False
    mock_task1.cancel.assert_called_once()
    mock_task2.cancel.assert_called_once()
    assert len(task_workflow_instance.tasks) == 0

@pytest.mark.asyncio
async def test_cleanup_handles_already_done_tasks(task_workflow_instance, mocker):
    """Test cleanup doesn't try to cancel tasks that are already done."""
    mock_task_done = AsyncMock(spec=asyncio.Task) # Was MagicMock, revert to AsyncMock for consistency if it has async methods
    mock_task_done.done.return_value = True 
    mock_task_done.cancel = MagicMock(name="cancel_mock_task_done") 

    mock_task_not_done = AsyncMock(spec=asyncio.Task)
    mock_task_not_done.done.return_value = False
    mock_task_not_done.side_effect = async_raiser_cancelled_error_side_effect # Use async helper
    mock_task_not_done.cancel = MagicMock(name="cancel_mock_task_not_done")
    
    task_workflow_instance.tasks = [mock_task_done, mock_task_not_done]
    task_workflow_instance.running = True
    
    await task_workflow_instance.cleanup()
    
    assert task_workflow_instance.running is False
    mock_task_done.cancel.assert_not_called()
    mock_task_not_done.cancel.assert_called_once()
    assert len(task_workflow_instance.tasks) == 0

@pytest.mark.asyncio
async def test_cleanup_handles_exception_during_task_processing(task_workflow_instance, mocker):
    """Test cleanup logs an error if an unexpected exception occurs during task cancellation/awaiting."""
    mock_logger_error = mocker.patch("app.bot.application.workflows.task_workflow.logger.error")
    
    # Revert to original working AsyncMock for this specific test case for RuntimeError
    mock_task = AsyncMock(spec=asyncio.Task)
    mock_task.done.return_value = False
    mock_task.cancel = MagicMock(name="cancel_mock_task_runtime") # Ensure cancel is a mock
    mock_task.side_effect = RuntimeError("Unexpected error during task await!")
    
    task_workflow_instance.tasks = [mock_task]
    task_workflow_instance.running = True
    
    await task_workflow_instance.cleanup()
    
    assert task_workflow_instance.running is False
    mock_task.cancel.assert_called_once()
    assert len(task_workflow_instance.tasks) == 0 
    mock_logger_error.assert_any_call("Error cleaning up task workflow: Unexpected error during task await!")

# --- Test register_background_tasks (Placeholder) ---
# The current implementation of register_background_tasks is empty.
# If tasks were actually created, we'd test that asyncio.create_task was called
# and the task was added to self.tasks.

def test_register_background_tasks_exists(task_workflow_instance):
    """Ensures the method exists, even if it does nothing yet."""
    assert hasattr(task_workflow_instance, 'register_background_tasks')
    # Can add a call to it, though it won't do anything yet
    task_workflow_instance.register_background_tasks() 
    assert len(task_workflow_instance.tasks) == 0 # Should remain empty

# --- Test some_background_task (Example Task - more involved to test properly) ---
# Testing the behavior of 'some_background_task' would require more setup,
# like patching asyncio.sleep and checking logger calls within a loop.
# For now, this is out of scope unless register_background_tasks actually uses it.

# Example of how one might start testing it if it were registered:
@pytest.mark.asyncio
async def test_some_background_task_loop_and_log(task_workflow_instance, mocker):
    """Basic check for the example background task's logging and sleep pattern."""
    mock_logger_debug = mocker.patch("app.bot.application.workflows.task_workflow.logger.debug")
    mock_asyncio_sleep = mocker.patch("asyncio.sleep", new_callable=AsyncMock)
    
    # To test this, we'd need to run it and stop it
    # Temporarily set running to True for the test scope if not using initialize()
    task_workflow_instance.running = True 
    
    # Run the task for a short duration or a few iterations
    # We need a way to break out of the 'while self.running' loop
    # For this test, we'll control 'running' and 'asyncio.sleep'
    
    async def side_effect_sleep(*args, **kwargs):
        # After the first sleep, set running to False to exit the loop
        task_workflow_instance.running = False
        # We still need to await something, or raise CancelledError
        # For simplicity, just return.
        return

    mock_asyncio_sleep.side_effect = side_effect_sleep
    
    # Directly call the task method. In a real scenario, it would be an asyncio.Task.
    await task_workflow_instance.some_background_task() 
    
    mock_logger_debug.assert_any_call("Running background task")
    mock_asyncio_sleep.assert_called_with(60) # Check it tried to sleep
    assert task_workflow_instance.running is False # Ensure it was set to False by the sleep side_effect

@pytest.mark.asyncio
async def test_some_background_task_handles_cancellation(task_workflow_instance, mocker):
    """Test that some_background_task handles asyncio.CancelledError gracefully."""
    mock_logger_info = mocker.patch("app.bot.application.workflows.task_workflow.logger.info")
    mock_asyncio_sleep = mocker.patch("asyncio.sleep", new_callable=AsyncMock)
    
    # Make sleep raise CancelledError on the first call
    mock_asyncio_sleep.side_effect = asyncio.CancelledError("Test Cancellation")
    
    task_workflow_instance.running = True
    await task_workflow_instance.some_background_task()
    
    mock_logger_info.assert_called_with("Background task cancelled")
    mock_asyncio_sleep.assert_called_once() # It should attempt to sleep once