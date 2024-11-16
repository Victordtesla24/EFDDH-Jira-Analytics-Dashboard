// src/AIAgent/Models/SystemMetrics.cs
namespace AIAgent.Models;

public record SystemMetrics
{
    public double MemoryUsageMb { get; init; }
    public double CpuTimeMs { get; init; }
    public int ThreadCount { get; init; }
    public double UptimeMinutes { get; init; }
    public string Status { get; init; } = "Unknown";
    public string? Error { get; init; }
    public Dictionary<string, double> JiraMetrics { get; init; } = new();

    public bool IsHealthy => Status == "Healthy" && Error == null;
}