// src/AIAgent/Services/AIAgentInteraction.cs
using Microsoft.Extensions.Logging;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace AIAgent.Services;

public interface IAIAgentInteraction
{
    Task<bool> ProposeAndAutoFix(string issue, string suggestion, Func<Task> fixAction);
}

public class AIAgentInteraction : IAIAgentInteraction
{
    private readonly ILogger<AIAgentInteraction> _logger;
    private readonly StateManager _stateManager;
    private readonly CancellationTokenSource _cts;

    public AIAgentInteraction(ILogger<AIAgentInteraction> logger, StateManager stateManager)
    {
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        _stateManager = stateManager ?? throw new ArgumentNullException(nameof(stateManager));
        _cts = new CancellationTokenSource();
    }

    public async Task<bool> ProposeAndAutoFix(string issue, string suggestion, Func<Task> fixAction)
    {
        _logger.LogWarning(@"
🤖 AI Agent detected an issue:
Issue: {Issue}
Suggestion: {Suggestion}
Auto-fixing in 10s...", issue, suggestion);

        await Task.Delay(10000, _cts.Token);
        await _stateManager.UpdateState("Auto-fixing");
        await fixAction();
        return true;
    }

    public void CancelFix()
    {
        _cts.Cancel();
    }
}