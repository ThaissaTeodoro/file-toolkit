# Guia de Testes - normalization_utils

Este guia explica como executar e interpretar os testes da biblioteca `normalization_utils`.

## 📁 Estrutura dos Arquivos

```
normalization_utils/
├── normalization_utils.py                 # Biblioteca principal
├── test_normalization_utils.py            # Testes unitários e de integração
├── test_normalization_utils_performance.py # Testes de performance (opcional)
├── conftest.py                     # Configuração pytest (SparkSession, fixtures)
├── pytest.ini                      # Configuração do pytest
├── test-requirements.txt           # Dependências para testes
├── run_tests.py                    # Script Python para facilitar execução
├── Makefile                        # Comandos automatizados (lint, test, cov, etc)
└── GUIA_TESTES.md 
```

## 🚀 Execução Rápida

### Opção 1: Usando Makefile (Recomendado)
```bash
# Instalar dependências
make install

# Executar todos os testes
make test

# Executar com cobertura de código
make test-cov

# Executar testes em paralelo
make test-parallel
```

### Opção 2: Usando o script Python
```bash
# Instalar dependências e executar testes
python run_tests.py --install-deps --coverage

# Executar apenas testes rápidos
python run_tests.py --markers "not slow"
```

### Opção 3: Usando pytest diretamente
```bash
# Instalar dependências
pip install -r test-requirements.txt

# Executar testes básicos
pytest test_normalization_utils.py -v

# Executar com cobertura
pytest test_normalization_utils.py --cov=json_utils --cov-report=html -v
```

## 📊 Tipos de Testes

### 1. Testes Unitários
Testam funções individuais isoladamente:
```bash
# Executar apenas testes unitários
make test-unit
# ou
pytest -m "unit" -v
```

**Cobertura:**
- ✅ `normalize_strings()`
- ✅ `normalize_column_names()` 
- ✅ `safe_string_to_double_spark()` 
- ✅ `get_logger()`

### 2. Testes de Integração
Testam fluxos completos combinando múltiplas funções:
```bash
# Executar apenas testes de integração
make test-integration
# ou
pytest -m "integration" -v
```

**Cenários testados:**
- Normalização + conversão em pipelines
- DataFrames com múltiplos tipos de dados

### 3. Testes de Performance
Verificam performance e escalabilidade:
```bash
# Executar testes de performance (podem demorar)
pytest test_normalization_utils_performance.py -v

# Pular testes lentos
pytest -m "not slow" -v
```

**Métricas avaliadas:**
- ⏱️ Tempo de execução para datasets grandes (1000+ registros)
- 🔄 Throughput (registros/segundo)
- 💾 Uso de memória
- 📈 Escalabilidade com diferentes tamanhos de dados

## 🏷️ Marcadores (Markers)
Os testes usam marcadores para categorização:

| Marcador | Descrição | Exemplo de Uso |
|----------|-----------|----------------|
| `unit` | Testes unitários | `pytest -m unit` |
| `integration` | Testes de integração | `pytest -m integration` |
| `slow` | Testes que demoram (>5s) | `pytest -m "not slow"` |
| `spark` | Testes que usam SparkSession | `pytest -m spark` |
| `performance` | Testes de performance | `pytest -m performance` |
| `stress` | Testes de stress (muito pesados) | `pytest -m stress` |

## 📈 Relatórios de Cobertura

### Visualizar Cobertura HTML
```bash
make test-cov
# Abrir htmlcov/index.html no navegador
```

### Meta de Cobertura
- **Atual:** 95%+ 
- **Mínimo aceitável:** 80%
- **Arquivos cobertos:** `normalization_utils.py`

## 🔧 Cenários de Teste Específicos

### Testes de Edge Cases
```bash
# Testar comportamento com dados problemáticos
pytest test_normalization_utils.py::TestEdgeCases -v
```

**Casos cobertos:**
- Colunas inexistentes
- Valores nulos/vazios
- Colunas não-string
- DataFrames sem colunas

### Testes de Tipos de Dados
```bash
# Testar conversões de tipos
pytest test_normalization_utils.py::TestSafeStringToDoubleSpark::test_various_formats -v
```

**Tipos testados:**
- `strings` com número em diferentes formatos
- `strings` com texto, vírgula, ponto, símbolo, etc

### Testes de Performance por Tamanho
```bash
# Testar escalabilidade
pytest test_normalization_utils_performance.py::TestScalability -v
```

**Cenários de escalabilidade:**
- 100, 500, 1000 registros
- 2, 3, 4 níveis de aninhamento
- Throughput mínimo: 50 registros/segundo

## 🐛 Debugging e Troubleshooting

### Executar em Modo Debug
```bash
# Debug com breakpoints
make test-debug
# ou
pytest --pdb -v

# Executar teste específico em debug
pytest test_json_utils.py::TestExtractJsonFields::test_extract_basic_fields --pdb -v
```

### Logs Detalhados
```bash
# Ver logs durante execução
pytest --log-cli-level=DEBUG -s -v

# Capturar saída completa
pytest --capture=no -v
```

### Problemas Comuns

#### 1. SparkSession não inicializa
**Erro:** `Exception: Could not find valid SPARK_HOME`
**Solução:**
```bash
# Instalar PySpark localmente
pip install pyspark

# Ou definir SPARK_HOME
export SPARK_HOME=/path/to/spark
```

#### 2. Testes lentos demais
**Erro:** Testes demoram muito para executar
**Solução:**
```bash
# Pular testes lentos
pytest -m "not slow" -v

# Executar em paralelo
pytest -n auto -v
```

#### 3. Problemas de memória
**Erro:** `java.lang.OutOfMemoryError`
**Solução:**
```bash
# Aumentar memória do Spark
export SPARK_DRIVER_MEMORY=2g
export SPARK_EXECUTOR_MEMORY=2g
```

#### 4. Falhas intermitentes
**Erro:** Testes passam/falham aleatoriamente
**Solução:**
```bash
# Executar múltiplas vezes
pytest --count=3 -v

# Verificar concorrência
pytest -x -v  # Para no primeiro erro
```

## 📊 Interpretando Resultados

### Output Normal de Sucesso
```
========================= test session starts =========================
test_json_utils.py::TestExtractJsonFields::test_extract_basic_fields PASSED [12%]
test_json_utils.py::TestFlattenJsonColumns::test_flatten_nested_struct PASSED [25%]
...
========================= 48 passed in 12.34s =========================

Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
json_utils.py          156      8    95%   23-24, 87, 142-145
--------------------------------------------------
TOTAL                  156      8    95%
```

### Métricas de Performance Esperadas
```
Extração de 1000 registros: 5.23s
Throughput: 191 rec/s ✅ (> 50 rec/s)
Uso de memória - Inicial: 245.2MB, Final: 267.8MB
Incremento: 22.6MB ✅ (< 200MB)
```

### Sinais de Alerta
❌ **Cobertura < 80%** - Adicionar mais testes
❌ **Throughput < 50 rec/s** - Otimizar performance
❌ **Incremento memória > 200MB** - Possível vazamento
❌ **Tempo > 30s para 1000 registros** - Performance degradada

## 🚀 CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Run tests
        run: make test-ci
```

### Pipeline Completa
```bash
# Executar pipeline completa (lint + format + test + coverage)
make quality-check
```

**Pipeline inclui:**
1. ✅ Linting com flake8
2. ✅ Formatação com black
3. ✅ Testes unitários e integração
4. ✅ Cobertura de código (>80%)
5. ✅ Relatórios HTML

## 📝 Adicionando Novos Testes

### Template para Novo Teste
```python
def test_nova_funcionalidade(self, spark, sample_data):
    """Testa nova funcionalidade específica."""
    # Arrange - Preparar dados
    df = spark.createDataFrame(sample_data, ["json_data"])
    expected_result = {...}
    
    # Act - Executar função
    result = nova_funcao(df, parametros)
    
    # Assert - Verificar resultado
    assert result.count() == expected_count
    assert result.collect()[0]["campo"] == expected_value
```

### Checklist para Novos Testes
- [ ] Nome descritivo (`test_funcao_cenario`)
- [ ] Docstring explicando o teste
- [ ] Dados de entrada válidos
- [ ] Verificação de resultado esperado
- [ ] Tratamento de edge cases
- [ ] Marcadores apropriados
- [ ] Performance aceitável

## 🔄 Execução Contínua

### Watch Mode (Desenvolvimento)
```bash
# Reexecutar testes quando arquivos mudarem
make test-watch
# ou 
pytest --looponfail
```

### Testes Específicos Durante Desenvolvimento
```bash
# Testar apenas função específica
pytest -k "extract_json_fields" -v

# Testar classe específica
pytest test_json_utils.py::TestExtractJsonFields -v

# Testar método específico
pytest test_json_utils.py::TestExtractJsonFields::test_extract_basic_fields -v
```

## 📞 Suporte

### Logs de Debug
Se encontrar problemas, execute com logs detalhados:
```bash
pytest --log-cli-level=DEBUG --tb=long -v > test_debug.log 2>&1
```

### Informações do Ambiente
```bash
# Versões instaladas
pip list | grep -E "(pyspark|pytest)"

# Configuração do Spark
python -c "from pyspark.sql import SparkSession; print(SparkSession.builder.getOrCreate().version)"
```

### Limpeza Completa
```bash
# Limpar todos os caches e arquivos temporários
make clean

# Reinstalar dependências
pip uninstall -y pyspark pytest
pip install -r test-requirements.txt
```

---

## 🎯 Resumo dos Comandos Principais

| Ação | Comando |
|------|---------|
| **Setup inicial** | `make install` |
| **Testes básicos** | `make test` |
| **Com cobertura** | `make test-cov` |
| **Apenas rápidos** | `make test-fast` |
| **Pipeline completa** | `make quality-check` |
| **Debug** | `make test-debug` |
| **Limpeza** | `make clean` |

**🎉 Pronto! Agora você tem uma suíte de testes completa para sua biblioteca json_utils.**