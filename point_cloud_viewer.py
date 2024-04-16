import zipfile
import io
import struct
import numpy as np

def extract_point_cloud_data(archivo_zon):
    # Abre el archivo .zon y lee los datos
    with open(archivo_zon, 'rb') as file:
        bArray = file.read()

    # Extrae el tamaño del área DIB
    nDIBSize = int.from_bytes(bArray[4:8], byteorder='little')
    bArrayZip = bArray[nDIBSize + 8:]

    # Abre el archivo comprimido contenido dentro del archivo .zon
    with zipfile.ZipFile(io.BytesIO(bArrayZip), 'r') as zip_ref:
        for entry in zip_ref.infolist():
            with zip_ref.open(entry) as file:
                # Procesa solo los archivos de tamaño significativo
                if entry.file_size > 100:
                    data = file.read()
                    # Desempaqueta datos de la cabecera
                    nWidth, nHeight, nElementSize, nRowBytes = struct.unpack_from('<IIII', data)
                    nExtraBytes = nRowBytes - (nWidth * nElementSize)
                    idx = 16  # Índice inicial después de la cabecera

                    if nElementSize == 4:  # Datos de altura
                        z_data = []
                        for y in range(nHeight):
                            row = []
                            for x in range(nWidth):
                                value, = struct.unpack_from('<I', data, idx)
                                row.append(value)
                                idx += 4
                            z_data.append(row)
                            idx += nExtraBytes

    # Crea una imagen a partir de los datos de altura
    img = np.zeros((len(z_data), len(z_data[0])))
    for idx, fila in enumerate(z_data):
        img[idx, :] = np.array(fila)

    return img  # Devuelve la imagen
