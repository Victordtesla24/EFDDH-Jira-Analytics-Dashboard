// Services/ErrorHandler.cs
namespace AIAgent.Services;

public class ErrorHandler
{
    private readonly ILogger<ErrorHandler> _logger;
    private readonly StateManager _stateManager;

    public ErrorHandler(ILogger<ErrorHandler> logger, StateManager stateManager)
    {
        _logger = logger;
        _stateManager = stateManager;
    }

    public async Task HandleError(Exception ex, string context)
    {
        _logger.LogError(ex, $"Error in {context}");
        await _stateManager.UpdateState($"Error: {context}");
    }
}