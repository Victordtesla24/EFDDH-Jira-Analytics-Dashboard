// Services/StateManager.cs
using AIAgent.Models;
using Microsoft.Extensions.Logging;

namespace AIAgent.Services;

public class StateManager
{
    private readonly AgentState _state;
    private readonly ILogger<StateManager> _logger;

    public StateManager(ILogger<StateManager> logger)
    {
        _state = new AgentState();
        _logger = logger;
    }

    public virtual async Task UpdateState(string status, Dictionary<string, double>? metrics = null)
    {
        await Task.Run(() =>
        {
            _state.Status = status;
            _state.LastUpdate = DateTime.UtcNow;
            if (metrics != null)
            {
                _state.Metrics = metrics;
            }
            _logger.LogInformation($"State updated: {status}");
        });
    }

    public virtual AgentState GetCurrentState() => _state;
}