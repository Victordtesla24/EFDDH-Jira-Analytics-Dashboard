using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using AIAgent.Models;

namespace AIAgent.Services
{
    public interface IMetricsCollector
    {
        Task<SystemMetrics> CollectMetricsAsync(CancellationToken cancellationToken = default);
        Dictionary<string, double> ConvertToDictionary(SystemMetrics metrics);
    }
}