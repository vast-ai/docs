import torch

def allocate_95_percent_gpu_memory(device: str = "cuda:0"):
    try:
        torch.cuda.empty_cache()
        device_properties = torch.cuda.get_device_properties(device)
        total_memory = device_properties.total_memory

        # Calculate 95% of total memory
        target_memory = int(total_memory * 0.95)

        # Each float32 element is 4 bytes
        num_elements = target_memory // 4

        # Create a tensor with the total number of elements
        # Since we need a 2D tensor, compute side length
        side_length = int(num_elements ** 0.5)

        tensor = torch.zeros((side_length, side_length),
                             dtype=torch.float32,
                             device=device)
        return tensor

    except RuntimeError as e:
        print(f"Runtime error during memory allocation on {device}: {str(e)}")
        return None

def test_ecc_on_all_gpus():
    try:
        num_gpus = torch.cuda.device_count()
        # Zero visible GPUs is a real failure mode (CUDA_VISIBLE_DEVICES=""
        # or all devices excluded by cgroup), not a vacuous pass — return
        # non-zero so the harness reports it rather than silently skipping
        # the test and claiming success.
        if num_gpus == 0:
            print("No GPUs detected.")
            return 1

        for i in range(num_gpus):
            device = f'cuda:{i}'
            print(f"Allocating memory on {device}...")

            tensor = allocate_95_percent_gpu_memory(device)
            if tensor is None:
                print(f"Failed to allocate memory on {device}.")
                return 1  # Indicate failure if allocation fails

            print(f"Memory allocation successful on {device}.")

        return 0  # Indicate success if all allocations succeed
    except Exception as e:
        print(f"An error occurred during ECC test: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = test_ecc_on_all_gpus()
    exit(exit_code)
