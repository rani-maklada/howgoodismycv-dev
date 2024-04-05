import subprocess

def render_resume(input_json_path, output_html_path):
    try:
        command = f"npx resumed render {input_json_path} --theme jsonresume-theme-even -o {output_html_path}"
        process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        if process.returncode == 0:
            return (True, "Resume rendered successfully.")
        else:
            return (False, f"An error occurred: {process.stderr}")
    except subprocess.CalledProcessError as e:
        return (False, f"An error occurred while running the command: {e.stderr}")
    except Exception as e:
        return (False, f"An unexpected error occurred: {str(e)}")
