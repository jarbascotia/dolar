# Microsserviço de Dólar

API para gestão de investimentos em dólar, com cálculo automático de taxas e lucro.

## 🛠 Rotas Disponíveis
| Método | Rota               | Descrição                       |
|--------|--------------------|---------------------------------|
| GET    | `/api/dolar`       | Listar todos os registros       |
| POST   | `/api/dolar`       | Adicionar nova compra           |
| PUT    | `/api/dolar/{id}`  | Editar registro                 |
| DELETE | `/api/dolar/{id}`  | Excluir registro                |

## 🐳 Execução com Docker
```bash
docker build -t dolar .
docker run -p 3004:3004 dolar

API Externa
AwesomeAPI: Cotação atualizada do USD-BRL.

