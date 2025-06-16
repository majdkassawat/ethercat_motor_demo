using Allure.NUnit;
using NUnit.Framework;
using HardwareInterface;
using System.Threading.Tasks;

namespace IntegrationTests
{
    [AllureNUnit]
    [AllureSuite("HW‑in‑the‑loop")]
    public class DeviceIntegrationTests
    {
        private DeviceController? _device;

        [SetUp]
        public async Task Setup()
        {
            Environment.SetEnvironmentVariable("SIMULATION", "1");
            _device = new DeviceController();
            await _device.ConnectAsync();
        }

        [TearDown]
        public void Teardown() => _device?.Dispose();

        [Test]
        [AllureTag("smoke")]
        public async Task SelfTestShouldPass()
        {
            var result = await _device!.RunSelfTestAsync();
            Assert.That(result, Is.EqualTo("OK"), "Self‑test must return OK.");
        }

        [Test]
        [AllureTag("motion")]
        public async Task DemoScriptReportsPosition()
        {
            var pos = await _device!.RunDemoAsync();
            Assert.That(pos, Is.GreaterThanOrEqualTo(0), "demo.py should print actual position");
        }
    }
}
