from ssh_utils import run_ssh_command
from gpu_parser import parse_gpu_process_mapping, get_username_by_pid
from time import sleep

def main():
    machine_list = ["GPU1", "GPU2", "GPU3", "GPU4", "GPU5", "GPU6", "GPU7"]
    # machine_list = ["GPU1", "GPU2", "GPU3", "GPU4", "GPU5", "GPU6", "GPU7", "GPU200", "GPU201", "GPU202"]

    for machine in machine_list:
        print(f"\n{'=' * 10} {machine} {'=' * 10}")

        try:
            # 1. GPU index と UUID の対応
            gpu_cmd = "nvidia-smi --query-gpu=index,uuid --format=csv,noheader"
            index_output = run_ssh_command(machine, gpu_cmd)
            sleep(1)

            # 2. UUID と PID の対応
            apps_cmd = "nvidia-smi --query-compute-apps=gpu_uuid,pid --format=csv,noheader"
            apps_output = run_ssh_command(machine, apps_cmd)

            # 3. GPU index → PID のマッピング
            mapping = parse_gpu_process_mapping(index_output, apps_output)

            # 4. 各GPUの使用状況とユーザー表示
            for gpu_index, pid in mapping.items():
                if pid is None:
                    print(f"GPU{gpu_index}: 空き")
                else:
                    user = get_username_by_pid(machine, pid)
                    if user:
                        print(f"GPU{gpu_index}: 使用中 by {user} (PID {pid})")
                    else:
                        print(f"GPU{gpu_index}: 使用中（ユーザー不明） (PID {pid})")

        except Exception as e:
            print(f"[エラー] {machine} の取得に失敗しました: {e}")


if __name__ == "__main__":
    main()
