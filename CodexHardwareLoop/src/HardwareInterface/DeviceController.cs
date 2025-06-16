using System;
using System.Threading.Tasks;

namespace HardwareInterface
{
    /// <summary>
    /// Thin façade around your real‑world HW API.
    /// Replace the mock implementations with actual HW calls.
    /// </summary>
    public sealed class DeviceController : IDisposable
    {
        public ValueTask ConnectAsync()
        {
            Console.WriteLine("[HW] Connecting to robot…");
            // TODO: replace with real connection logic
            return ValueTask.CompletedTask;
        }

        public async ValueTask<string> RunSelfTestAsync()
        {
            Console.WriteLine("[HW] Running self‑test.");
            await Task.Delay(500); // simulate latency
            // TODO: collect real diagnostic output
            return "OK";
        }

        public void Dispose() => Console.WriteLine("[HW] Disconnected.");
    }
}
