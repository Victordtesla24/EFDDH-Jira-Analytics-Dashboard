// Models/AgentState.cs
namespace AIAgent.Models;

public class AgentState
{
    public int Id { get; set; }
    public string Status { get; set; } = string.Empty;
    public DateTime LastUpdate { get; set; }
    public int ProcessedFiles { get; set; }
    public Dictionary<string, double> Metrics { get; set; } = new();
}