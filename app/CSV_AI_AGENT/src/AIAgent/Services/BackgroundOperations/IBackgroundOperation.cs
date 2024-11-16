// src/AIAgent/Services/BackgroundOperations/IBackgroundOperation.cs
namespace AIAgent.Services.BackgroundOperations;

public interface IBackgroundOperation
{
    Task ExecuteAsync(CancellationToken cancellationToken);
    Task HandleErrorAsync(Exception ex, string context);
}