// src/AIAgent/Models/IJiraItem.cs
namespace AIAgent.Models;

public interface IJiraItem
{
      string IssueKey { get; init; }
    string IssueType { get; init; }
    string Priority { get; init; }
    string? Status { get; init; }
    string? Assignee { get; init; }
    string? StoryPoints { get; init; }
    string? Epic { get; init; }
    string? EpicIssueKey { get; init; }
}