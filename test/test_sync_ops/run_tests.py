#!/usr/bin/env python3
"""
Script para executar os testes do window com diferentes configurações.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description=""):
    """Executa um comando e retorna o código de saída."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"Executando: {' '.join(cmd)}")
    print(f"{'='*60}")

    result = subprocess.run(cmd)
    return result.returncode

def setup_environment():
    """Configura o ambiente para os testes."""
    current_dir = Path(__file__).parent.absolute()
    python_path = os.environ.get('PYTHONPATH', '')
    if str(current_dir) not in python_path.split(':'):
        os.environ['PYTHONPATH'] = f"{current_dir}:{python_path}".rstrip(':')

    os.environ.setdefault('PYSPARK_PYTHON', sys.executable)
    os.environ.setdefault('PYSPARK_DRIVER_PYTHON', sys.executable)

    print(f"✅ Ambiente configurado:")
    print(f"   - PYTHONPATH: {os.environ['PYTHONPATH']}")
    print(f"   - PYSPARK_PYTHON: {os.environ['PYSPARK_PYTHON']}")

def main():
    parser = argparse.ArgumentParser(description="Executor de testes para window")
    parser.add_argument('--coverage', action='store_true', help='Executa testes com cobertura de código')
    parser.add_argument('--parallel', action='store_true', help='Executa testes em paralelo')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso')
    parser.add_argument('--markers', '-m', type=str, help='Executa apenas testes com marcadores específicos')
    parser.add_argument('--test-file', '-f', type=str, help='Executa apenas um arquivo de teste específico')
    parser.add_argument('--install-deps', action='store_true', help='Instala dependências antes de executar testes')
    args = parser.parse_args()

    setup_environment()

    if args.install_deps:
        install_cmd = [sys.executable, '-m', 'pip', 'install', '-r', 'test-requirements.txt']
        if run_command(install_cmd, "Instalando dependências") != 0:
            print("❌ Falha na instalação das dependências")
            return 1

    pytest_cmd = [sys.executable, '-m', 'pytest']

    if args.coverage:
        pytest_cmd.extend([
            '--cov=window_utils',
            '--cov-report=html',
            '--cov-report=term-missing',
            '--cov-fail-under=80'
        ])

    if args.parallel:
        pytest_cmd.extend(['-n', 'auto'])  # pytest-xdist

    if args.verbose:
        pytest_cmd.append('-vv')

    if args.markers:
        pytest_cmd.extend(['-m', args.markers])

    # Define o arquivo/diretório de teste
    if args.test_file:
        pytest_cmd.append(args.test_file)
    else:
        # Por padrão roda todos os testes iniciados por test_*
        pytest_cmd.append('sync_ops.py')

    # Executa os testes
    exit_code = run_command(pytest_cmd, "Executando testes")

    if exit_code == 0:
        print("\n🎉 Todos os testes passaram!")
        if args.coverage:
            print("📊 Relatório de cobertura gerado em htmlcov/index.html")
    else:
        print(f"\n❌ Testes falharam (código de saída: {exit_code})")

    return exit_code

if __name__ == "__main__":
    sys.exit(main())
