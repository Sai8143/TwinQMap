import asyncio
from qiskit_ibm_runtime import QiskitRuntimeService

async def test_ibm():
    token = "e4UV8XMFASmSGbhF5EuxCPCcZGEafEGlZpwOF3SR3juf"
    try:
        print("Authenticating with IBM Quantum Service...")
        service = QiskitRuntimeService(token=token)
        print("Authenticated successfully. Listing all available backends...")
        backends = service.backends()
        for b in backends:
            print(f"- {b.name}: {b.num_qubits} qubits")
    except Exception as e:
        print(f"Error checking IBM Quantum: {e}")

if __name__ == "__main__":
    asyncio.run(test_ibm())
