# =============================================================================
# BLOQUE 1: IMPORTACIONES
# =============================================================================
# Aquí traemos las "herramientas" que Python no tiene por defecto.
# Es como abrir la caja de herramientas antes de empezar a trabajar.

import json              # Para leer y escribir archivos JSON
import os                # Para interactuar con el sistema operativo (limpiar pantalla)
from datetime import datetime  # Para obtener fechas y horas automáticas
from rich.console import Console  # Para colores y formato en la terminal
from rich.table import Table      # Para crear tablas bonitas

# Creamos un objeto "consola" que usaremos para imprimir con colores
console = Console()


# =============================================================================
# BLOQUE 2: VARIABLES GLOBALES
# =============================================================================
# Las listas que almacenarán toda la información de la app.
# Son "globales" porque todas las funciones necesitan acceder a ellas.

lista_domicilios = []
lista_gastos = []


# =============================================================================
# BLOQUE 3: FUNCIONES AUXILIARES (HERRAMIENTAS REUTILIZABLES)
# =============================================================================
# Estas funciones son como "herramientas de taller" que usamos en varios lugares.

def limpiar_pantalla():
    """Limpia la terminal según el sistema operativo."""
    os.system('cls' if os.name == 'nt' else 'clear')


def pedir_numero_positivo(mensaje):
    """Solicita un número entero positivo. Repite hasta que sea válido."""
    while True:
        try:
            valor = int(input(mensaje))
            if valor < 0:
                console.print("[red]⚠️ El valor no puede ser negativo.[/red]")
                continue
            return valor
        except ValueError:
            console.print("[red]⚠️ Debe ingresar un número entero válido.[/red]")


def pedir_texto_no_vacio(mensaje):
    """Solicita un texto que no esté vacío. Nueva función de validación."""
    while True:
        texto = input(mensaje).strip()  # .strip() quita espacios al inicio/final
        if texto == "":
            console.print("[red]⚠️ El campo no puede estar vacío.[/red]")
            continue
        return texto


# =============================================================================
# BLOQUE 4: FUNCIONES DE PERSISTENCIA (GUARDAR Y CARGAR)
# =============================================================================
# Estas funciones manejan el archivo JSON, como un "archivero digital".

def guardar_datos():
    """Guarda las listas en el archivo JSON con formato legible."""
    try:
        diccionario_datos = {
            "domicilios": lista_domicilios,
            "gastos": lista_gastos
        }
        with open("datos_app.json", "w", encoding="utf-8") as archivo:
            # indent=4 hace que el JSON sea legible para humanos
            json.dump(diccionario_datos, archivo, indent=4, ensure_ascii=False)
        console.print("[green]✅ Datos guardados correctamente.[/green]")
    except Exception as e:
        console.print(f"[red]❌ Error al guardar: {e}[/red]")


def cargar_datos():
    """Carga los datos del archivo JSON al iniciar el programa."""
    global lista_domicilios, lista_gastos
    try:
        with open("datos_app.json", "r", encoding="utf-8") as archivo:
            datos_cargados = json.load(archivo)
        lista_domicilios = datos_cargados["domicilios"]
        lista_gastos = datos_cargados["gastos"]
        console.print(f"[green]✅ Datos cargados: {len(lista_domicilios)} domicilios, "
                      f"{len(lista_gastos)} gastos.[/green]")
    except FileNotFoundError:
        console.print("[yellow]⚠️ No existe el archivo. Iniciando con listas vacías.[/yellow]")
        lista_domicilios = []
        lista_gastos = []
    except json.JSONDecodeError:
        console.print("[yellow]⚠️ Archivo corrupto. Iniciando con listas vacías.[/yellow]")
        lista_domicilios = []
        lista_gastos = []
    except KeyError:
        console.print("[yellow]⚠️ Estructura incorrecta. Iniciando con listas vacías.[/yellow]")
        lista_domicilios = []
        lista_gastos = []


# =============================================================================
# BLOQUE 5: FUNCIONES DE REGISTRO
# =============================================================================
# Permiten al usuario agregar nuevos domicilios y gastos.

def registrar_domicilio():
    """Registra un nuevo domicilio con validación de datos."""
    console.print("\n[bold cyan]=== REGISTRAR DOMICILIO ===[/bold cyan]")
    
    direccion = pedir_texto_no_vacio("Dirección: ")
    valor = pedir_numero_positivo("Valor del domicilio: $")
    propina = pedir_numero_positivo("Propina: $")
    
    # Creamos un diccionario con todos los datos, incluyendo la fecha actual
    nuevo_domicilio = {
        "direccion": direccion,
        "valor": valor,
        "propina": propina,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")  # Fecha y hora automática
    }
    
    lista_domicilios.append(nuevo_domicilio)
    console.print(f"[green]✅ Domicilio registrado: {direccion}[/green]")
    guardar_datos()


def registrar_gasto():
    """Registra un nuevo gasto con validación de datos."""
    console.print("\n[bold cyan]=== REGISTRAR GASTO ===[/bold cyan]")
    
    concepto = pedir_texto_no_vacio("Concepto: ")
    valor = pedir_numero_positivo("Valor del gasto: $")
    
    nuevo_gasto = {
        "concepto": concepto,
        "valor": valor,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    lista_gastos.append(nuevo_gasto)
    console.print(f"[green]✅ Gasto registrado: {concepto}[/green]")
    guardar_datos()


# =============================================================================
# BLOQUE 6: FUNCIONES DE CONSULTA
# =============================================================================
# Muestran información al usuario de forma organizada.

def calcular_balance():
    """Calcula y muestra un reporte detallado del balance."""
    total_ingresos = sum(d["valor"] + d["propina"] for d in lista_domicilios)
    total_gastos = sum(g["valor"] for g in lista_gastos)
    balance = total_ingresos - total_gastos
    
    console.print("\n[bold cyan]" + "="*50 + "[/bold cyan]")
    console.print("[bold cyan]📊 REPORTE DE BALANCE[/bold cyan]")
    console.print("[bold cyan]" + "="*50 + "[/bold cyan]")
    console.print(f"[green]💰 Total ingresos: ${total_ingresos:,}[/green]")
    console.print(f"[red]💸 Total gastos: ${total_gastos:,}[/red]")
    console.print("-"*50)
    
    if balance > 0:
        console.print(f"[bold green]✅ Ganancia neta: ${balance:,}[/bold green]")
    elif balance < 0:
        console.print(f"[bold red]❌ Pérdida neta: ${abs(balance):,}[/bold red]")
    else:
        console.print("[bold yellow]⚖️ Balance en cero: $0[/bold yellow]")
    
    console.print("[bold cyan]" + "="*50 + "[/bold cyan]\n")
    return balance


def mostrar_domicilios():
    """Muestra todos los domicilios en una tabla organizada."""
    if not lista_domicilios:
        console.print("[yellow]⚠️ No hay domicilios registrados.[/yellow]")
        return
    
    # Creamos una tabla con columnas
    tabla = Table(title="📋 Lista de Domicilios")
    tabla.add_column("#", style="dim", width=4)
    tabla.add_column("Dirección", style="cyan")
    tabla.add_column("Valor", style="green", justify="right")
    tabla.add_column("Propina", style="yellow", justify="right")
    tabla.add_column("Total", style="bold", justify="right")
    tabla.add_column("Fecha", style="dim")
    
    for i, dom in enumerate(lista_domicilios, 1):
        total = dom["valor"] + dom["propina"]
        tabla.add_row(
            str(i),
            dom["direccion"],
            f"${dom['valor']:,}",
            f"${dom['propina']:,}",
            f"${total:,}",
            dom.get("fecha", "N/A")
        )
    
    console.print(tabla)


def mostrar_gastos():
    """Muestra todos los gastos en una tabla organizada."""
    if not lista_gastos:
        console.print("[yellow]⚠️ No hay gastos registrados.[/yellow]")
        return
    
    tabla = Table(title="💸 Lista de Gastos")
    tabla.add_column("#", style="dim", width=4)
    tabla.add_column("Concepto", style="red")
    tabla.add_column("Valor", style="yellow", justify="right")
    tabla.add_column("Fecha", style="dim")
    
    for i, gas in enumerate(lista_gastos, 1):
        tabla.add_row(
            str(i),
            gas["concepto"],
            f"${gas['valor']:,}",
            gas.get("fecha", "N/A")
        )
    
    console.print(tabla)


# =============================================================================
# BLOQUE 7: MENÚ PRINCIPAL
# =============================================================================
# El "cerebro" del programa. Controla el flujo de la aplicación.

def mostrar_menu():
    """Muestra el menú principal y retorna la opción elegida."""
    console.print("\n[bold cyan]" + "="*50 + "[/bold cyan]")
    console.print("[bold cyan]🏍️ SISTEMA DE DOMICILIOS Y GASTOS[/bold cyan]")
    console.print("[bold cyan]" + "="*50 + "[/bold cyan]")
    console.print("[white]1. 📝 Registrar domicilio[/white]")
    console.print("[white]2. 💸 Registrar gasto[/white]")
    console.print("[white]3. 📊 Ver balance total[/white]")
    console.print("[white]4. 📋 Ver lista de domicilios[/white]")
    console.print("[white]5. 🧾 Ver lista de gastos[/white]")
    console.print("[white]6. 🚪 Salir[/white]")
    console.print("[bold cyan]" + "="*50 + "[/bold cyan]")
    return input("\nSeleccione una opción: ")


def reporte_final():
    """Muestra el reporte final al salir del programa."""
    console.print("\n[bold cyan]" + "="*50 + "[/bold cyan]")
    console.print("[bold cyan]📊 REPORTE FINAL[/bold cyan]")
    console.print("[bold cyan]" + "="*50 + "[/bold cyan]")
    
    console.print(f"\n[bold]🏠 DOMICILIOS ({len(lista_domicilios)}):[/bold]")
    for i, dom in enumerate(lista_domicilios, 1):
        total = dom["valor"] + dom["propina"]
        console.print(f"   [dim]{i}.[/dim] {dom['direccion']} - [green]${total:,}[/green]")
    
    console.print(f"\n[bold]💸 GASTOS ({len(lista_gastos)}):[/bold]")
    for i, gas in enumerate(lista_gastos, 1):
        console.print(f"   [dim]{i}.[/dim] {gas['concepto']} - [red]${gas['valor']:,}[/red]")
    
    balance = sum(d["valor"] + d["propina"] for d in lista_domicilios) - sum(g["valor"] for g in lista_gastos)
    console.print(f"\n[bold]💰 BALANCE FINAL: ${balance:,}[/bold]")
    console.print("\n[bold green]✅ Programa finalizado correctamente.[/bold green]")
    console.print("[bold cyan]" + "="*50 + "[/bold cyan]\n")


# =============================================================================
# BLOQUE 8: PUNTO DE ENTRADA DEL PROGRAMA
# =============================================================================
# Aquí es donde TODO comienza. Es el "interruptor" de la app.

def main():
    """Función principal que coordina toda la aplicación."""
    limpiar_pantalla()
    console.print("[bold cyan]🚀 Iniciando sistema...[/bold cyan]")
    cargar_datos()
    
    while True:
        opcion = mostrar_menu()
        limpiar_pantalla()
        
        if opcion == "1":
            registrar_domicilio()
        elif opcion == "2":
            registrar_gasto()
        elif opcion == "3":
            calcular_balance()
        elif opcion == "4":
            mostrar_domicilios()
        elif opcion == "5":
            mostrar_gastos()
        elif opcion == "6":
            guardar_datos()
            reporte_final()
            break
        else:
            console.print("[red]❌ Opción no válida. Intente de nuevo.[/red]")
        
        # Pausa para que el usuario vea el resultado antes de volver al menú
        console.print("\n[dim]Presione Enter para continuar...[/dim]")
        input()
        limpiar_pantalla()


# Esta línea asegura que el programa solo se ejecute cuando lo corramos directamente
if __name__ == "__main__":
    main()

  