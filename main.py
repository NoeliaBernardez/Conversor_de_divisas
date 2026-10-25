
import sys
from typing import Any, Dict, List, Optional
import requests
from tabulate import tabulate

API_URL: str = "https://dolarapi.com/v1/dolares"
TIMEOUT_SECONDS: int = 10


def obtener_cotizaciones(url: str) -> List[Dict[str, Any]]:

    try:
        respuesta = requests.get(url, timeout=TIMEOUT_SECONDS)
        respuesta.raise_for_status()
        datos: List[Dict[str, Any]] = respuesta.json()
        return datos
    except requests.exceptions.Timeout as err:
        raise requests.RequestException("La conexión con la API superó el tiempo de espera.") from err
    except requests.exceptions.ConnectionError as err:
        raise requests.RequestException("No se pudo establecer conexión con el servidor.") from err
    except requests.exceptions.HTTPError as err:
        raise requests.RequestException(f"Error HTTP devuelto por la API: {err}") from err
    except requests.exceptions.RequestException as err:
        raise requests.RequestException(f"Error en la petición a la API: {err}") from err
    except ValueError as err:
        raise ValueError("La respuesta recibida no es un formato JSON válido.") from err


def pedir_monto_ars() -> float:

    while True:
        entrada: str = input("Ingrese el monto en Pesos Argentinos (ARS): ").strip()
        entrada_limpia = entrada.replace(".", "").replace(",", ".")
        try:
            monto: float = float(entrada)
            if monto <= 0:
                print("⚠️ El monto debe ser un número positivo mayor a cero.\n")
                continue
            return monto
        except ValueError:
            print("⚠️ Entrada inválida. Ingrese un número válido (ej: 15000 o 15000.50).\n")


def procesar_conversiones(
    cotizaciones: List[Dict[str, Any]], monto_ars: float
) -> List[List[str]]:

    casas_interes: Dict[str, str] = {
        "oficial": "Dólar Oficial",
        "blue": "Dólar Blue",
    }

    filas_tabla: List[List[str]] = []

    for item in cotizaciones:
        casa: Optional[str] = item.get("casa")
        if casa in casas_interes:
            try:
                nombre: str = casas_interes[casa]
                compra: float = float(item["compra"])
                venta: float = float(item["venta"])

                total_convertido: float = monto_ars / venta if venta > 0 else 0.0

                filas_tabla.append(
                    [
                        nombre,
                        f"$ {compra:,.2f}",
                        f"$ {venta:,.2f}",
                        f"USD {total_convertido:,.2f}",
                    ]
                )
            except (KeyError, TypeError, ValueError) as err:
                print(f"⚠️ Advertencia: Datos incompletos o corruptos para tipo '{casa}': {err}")

    return filas_tabla

def mostrar_resultados(filas: List[List[str]], monto_ars: float) -> None:
    if not filas:
        print("\n⚠️ No se encontraron cotizaciones para Oficial o Blue.")
        return

    encabezados: List[str] = ["Tipo de Dólar", "Compra (ARS)", "Venta (ARS)", f"Total con ${monto_ars:,.2f} ARS"]

    print("\n" + "=" * 60)
    print("           RESULTADO DE LA CONVERSIÓN DE DIVISAS")
    print("=" * 60)
    print(tabulate(filas, headers=encabezados, tablefmt="fancy_grid", stralign="center"))
    print("=" * 60 + "\n")


def main() -> None:
    print("--------------------------------------------------")
    print("   Conversor de Divisas ARS -> Dólar (En Vivo)   ")
    print("--------------------------------------------------\n")

    monto_ars: float = pedir_monto_ars()

    try:
        cotizaciones: List[Dict[str, Any]] = obtener_cotizaciones(API_URL)
        filas: List[List[str]] = procesar_conversiones(cotizaciones, monto_ars)
        mostrar_resultados(filas, monto_ars)
    except (requests.RequestException, ValueError) as error:
        print(f"\n❌ Error al obtener las cotizaciones: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()



    