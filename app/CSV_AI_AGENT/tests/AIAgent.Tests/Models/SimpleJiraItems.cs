// tests/AIAgent.Tests/Models/SimpleJiraItem.cs
namespace AIAgent.Tests.Models;

public class SimpleJiraItem
{
    public string IssueKey { get; set; } = string.Empty;
    public string IssueType { get; set; } = string.Empty;
    public string Priority { get; set; } = string.Empty;
}