CATEGORIAS = {
    "1": {"nombre": "Aseo del hogar",          "iva": 0.19, "saludable": 0.0},
    "2": {"nombre": "Cuidado personal",        "iva": 0.19, "saludable": 0.0},
    "3": {"nombre": "Lácteos (leche, queso, yogurt)", "iva": 0.0,  "saludable": 0.0},
    "4": {"nombre": "Carnes y embutidos",      "iva": 0.0,  "saludable": 0.0},
    "5": {"nombre": "Panadería, granos y cereales", "iva": 0.0, "saludable": 0.0},
    "6": {"nombre": "Bebidas (gaseosas, jugos, etc.)", "iva": 0.19, "saludable": 0.10},
    "7": {"nombre": "Snacks y confitería",     "iva": 0.19, "saludable": 0.10},
    "8": {"nombre": "Otros productos en general", "iva": 0.19, "saludable": 0.0},
}

DESCUENTO_TARJETA_TIENDA = 0.05  # 5% si paga con tarjeta de la tienda

def formato_pesos(valor):
    """Convierte un número a formato de pesos colombianos: $ 12.345"""
    return f"$ {valor:,.0f}".replace(",", ".")


def leer_numero(mensaje, permitir_decimales=True, minimo=0):
    """Pide un número al usuario validando que sea correcto."""
    while True:
        entrada = input(mensaje).strip().replace(",", ".")
        try:
            valor = float(entrada) if permitir_decimales else int(entrada)
            if valor < minimo:
                print(f"   -> El valor debe ser mayor o igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("   -> Por favor ingresa un número válido.")


def leer_si_no(mensaje):
    """Pide una respuesta sí/no y devuelve True o False."""
    while True:
        respuesta = input(mensaje).strip().lower()
        if respuesta in ("s", "si", "sí"):
            return True
        elif respuesta in ("n", "no"):
            return False
        else:
            print("   -> Responde solo con 's' (sí) o 'n' (no).")


def mostrar_categorias():
    """Muestra el menú de categorías disponibles."""
    print("\n¿Qué tipo de producto vas a registrar?")
    for clave, datos in CATEGORIAS.items():
        print(f"   {clave}. {datos['nombre']}")


def elegir_categoria():
    """Pide al cajero que elija una categoría válida."""
    mostrar_categorias()
    while True:
        opcion = input("Elige el número de la categoría: ").strip()
        if opcion in CATEGORIAS:
            return CATEGORIAS[opcion]
        print("   -> Opción no válida, intenta de nuevo.")


def registrar_producto():
    """Pide todos los datos de un producto y calcula sus valores."""
    print("\n--- NUEVO PRODUCTO ---")
    nombre = input("Nombre del producto: ").strip().title()

    categoria = elegir_categoria()

    precio_unitario = leer_numero("Precio unitario del producto: $ ")
    cantidad = leer_numero("Cantidad de unidades: ", permitir_decimales=False, minimo=1)

    # Descuento individual del producto
    porcentaje_descuento = 0.0
    if leer_si_no("¿Este producto tiene descuento o promoción? (s/n): "):
        porcentaje_descuento = leer_numero(
            "Ingresa el porcentaje de descuento (ej: 10 para 10%): ", minimo=0
        )

    # Cálculos del producto
    subtotal_bruto = precio_unitario * cantidad
    valor_descuento = subtotal_bruto * (porcentaje_descuento / 100)
    subtotal_neto = subtotal_bruto - valor_descuento

    valor_iva = subtotal_neto * categoria["iva"]

    # Impuesto saludable (solo aplica a bebidas/snacks que el cajero
    # confirme que son productos azucarados o ultraprocesados)
    valor_saludable = 0.0
    if categoria["saludable"] > 0:
        if leer_si_no(
            "¿Este producto está gravado con el impuesto saludable "
            "(bebida azucarada / ultraprocesado)? (s/n): "
        ):
            valor_saludable = subtotal_neto * categoria["saludable"]

    total_producto = subtotal_neto + valor_iva + valor_saludable

    producto = {
        "nombre": nombre,
        "categoria": categoria["nombre"],
        "precio_unitario": precio_unitario,
        "cantidad": cantidad,
        "subtotal_bruto": subtotal_bruto,
        "porcentaje_descuento": porcentaje_descuento,
        "valor_descuento": valor_descuento,
        "subtotal_neto": subtotal_neto,
        "tasa_iva": categoria["iva"],
        "valor_iva": valor_iva,
        "valor_saludable": valor_saludable,
        "total_producto": total_producto,
    }

    print(f"\n'{nombre}' agregado. Total de este producto: {formato_pesos(total_producto)}")
    return producto


def imprimir_factura(carrito, pago_con_tarjeta):
    print("\n" + "=" * 55)
    print("                  FACTURA DE VENTA")
    print("=" * 55)

    subtotal_general = 0.0
    descuento_general = 0.0
    iva_general = 0.0
    saludable_general = 0.0

    for producto in carrito:
        print(f"\nProducto:   {producto['nombre']}")
        print(f"Categoría:  {producto['categoria']}")
        print(f"Cantidad:   {producto['cantidad']}  x  "
              f"{formato_pesos(producto['precio_unitario'])}"
              f"  =  {formato_pesos(producto['subtotal_bruto'])}")

        if producto["porcentaje_descuento"] > 0:
            print(f"Descuento:  {producto['porcentaje_descuento']:.0f}%  "
                  f"(-{formato_pesos(producto['valor_descuento'])})")

        print(f"Subtotal:   {formato_pesos(producto['subtotal_neto'])}")

        if producto["tasa_iva"] > 0:
            print(f"IVA ({producto['tasa_iva']*100:.0f}%):  "
                  f"{formato_pesos(producto['valor_iva'])}")
        else:
            print("IVA: Producto exento (0%)")

        if producto["valor_saludable"] > 0:
            print(f"Impuesto saludable: {formato_pesos(producto['valor_saludable'])}")

        print(f"Total producto: {formato_pesos(producto['total_producto'])}")
        print("-" * 55)

        subtotal_general += producto["subtotal_neto"]
        descuento_general += producto["valor_descuento"]
        iva_general += producto["valor_iva"]
        saludable_general += producto["valor_saludable"]

    total_antes_tarjeta = subtotal_general + iva_general + saludable_general

    print("\nRESUMEN DE LA COMPRA")
    print(f"Subtotal de productos (con descuentos aplicados): "
          f"{formato_pesos(subtotal_general)}")
    print(f"Total descuentos aplicados:                       "
          f"-{formato_pesos(descuento_general)}")
    print(f"Total IVA:                                         "
          f"{formato_pesos(iva_general)}")
    if saludable_general > 0:
        print(f"Total impuesto saludable:                          "
              f"{formato_pesos(saludable_general)}")

    print(f"\nTOTAL A PAGAR (sin tarjeta de la tienda): "
          f"{formato_pesos(total_antes_tarjeta)}")

    total_final = total_antes_tarjeta
    if pago_con_tarjeta:
        descuento_tarjeta = total_antes_tarjeta * DESCUENTO_TARJETA_TIENDA
        total_final = total_antes_tarjeta - descuento_tarjeta
        print(f"Descuento tarjeta de la tienda (5%):       "
              f"-{formato_pesos(descuento_tarjeta)}")

    print("=" * 55)
    print(f"TOTAL FINAL A PAGAR: {formato_pesos(total_final)}")
    print("=" * 55)
    print("\n¡Gracias por su compra!")



def main():
    print("=" * 55)
    print("   BIENVENIDO AL SISTEMA DE CAJA - SUPERMERCADO")
    print("=" * 55)

    carrito = []

    while True:
        producto = registrar_producto()
        carrito.append(producto)

        if not leer_si_no("\n¿Deseas agregar otro producto? (s/n): "):
            break

    if not carrito:
        print("No se registraron productos. Finalizando programa.")
        return

    print("\nFORMA DE PAGO")
    pago_con_tarjeta = leer_si_no(
        "¿El cliente pagará con la tarjeta de la tienda "
        "(obtiene 5% de descuento)? (s/n): "
    )

    imprimir_factura(carrito, pago_con_tarjeta)


if __name__ == "__main__":
    main()