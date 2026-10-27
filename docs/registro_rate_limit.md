## Registro del ensayo de rate limit
 
- Fecha: 26-10-2026
- Peticiones enviadas: 10
- Petición donde apareció el primer 429: la número 10
- Esperas observadas: 2.2s, 4.2s (backoff exponencial con jitter, correcto)
- Costo total del ensayo: $0.00036
- Total tokens ensayo: 216
- Resultado: Petición 10 no conluida luego de fallar 3 veces

``` bash
python3 cliente.py
Operación: 24 tokens, costo estimado: $0.000040 (acumulado: $0.000040)
Respuesta 1: Los flamencos rosados obtienen su color comiendo camarones....
Operación: 23 tokens, costo estimado: $0.000038 (acumulado: $0.000078)
Respuesta 2: Las nutrias marinas se toman de las manos para no separarse....
Operación: 22 tokens, costo estimado: $0.000035 (acumulado: $0.000113)
Respuesta 3: Las nutrias se toman de las manos para no separarse....
Operación: 22 tokens, costo estimado: $0.000035 (acumulado: $0.000148)
Respuesta 4: Las nutrias se toman de las manos para no separarse....
Operación: 26 tokens, costo estimado: $0.000045 (acumulado: $0.000193)
Respuesta 5: Las nutrias marrones duermen tomadas de la mano para no separarse....
Operación: 24 tokens, costo estimado: $0.000040 (acumulado: $0.000234)
Respuesta 6: Los flamencos son rosados debido a su dieta de camarones....
Operación: 27 tokens, costo estimado: $0.000048 (acumulado: $0.000281)
Respuesta 7: Los flamencos rosados obtienen su color comiendo camarones y algas....
Operación: 24 tokens, costo estimado: $0.000040 (acumulado: $0.000322)
Respuesta 8: Los flamencos son rosados debido a los camarones que comen....
Operación: 24 tokens, costo estimado: $0.000040 (acumulado: $0.000362)
Respuesta 9: Los flamencos son rosados debido a su dieta de camarones....
Intento 1 de 3 falló. Reintentando en 2.2s...
Intento 2 de 3 falló. Reintentando en 4.2s...
Intento 3 de 3 falló.
Respuesta 10 falló definitivamente: El servicio no respondió tras varios intentos. Intenta más tarde.
Costo total del ensayo: $0.00036
Total tokens del ensayo: 216
```

- Fecha: 26-10-2026
- Peticiones enviadas: 10
- Petición donde apareció el primer 429: la número  y luego en la 7
- Esperas observadas: 2.0s, 4.0s - 2.2s, 4.1s (backoff exponencial con jitter, correcto)
- Costo total del ensayo: $0.00046
- Total tokens ensayo: 282
- Resultado: todas las peticiones terminaron con éxito tras reintentar

``` bash
python3 cliente.py
Operación: 30 tokens, costo estimado: $0.000051 (acumulado: $0.000051)
Respuesta 1: Las nutrias marinas duermen tomadas de la mano para no separarse con la corriente.
Operación: 27 tokens, costo estimado: $0.000043 (acumulado: $0.000094)
Respuesta 2: Las nutrias marinas se toman de las manos al dormir para no separarse.
Operación: 30 tokens, costo estimado: $0.000051 (acumulado: $0.000145)
Respuesta 3: Los flamencos son de color rosa porque se alimentan de camarones y algas.
Operación: 27 tokens, costo estimado: $0.000043 (acumulado: $0.000188)
Respuesta 4: Las nutrias marinas se toman de las patas al dormir para no separarse.
Intento 1 de 3 falló. Reintentando en 2.0s...
Intento 2 de 3 falló. Reintentando en 4.0s...
Operación: 27 tokens, costo estimado: $0.000043 (acumulado: $0.000231)
Respuesta 5: Las nutrias marinas se toman de las manos al dormir para no separarse.
Operación: 31 tokens, costo estimado: $0.000053 (acumulado: $0.000285)
Respuesta 6: Los flamencos son rosados porque comen camarones y algas llenas de pigmento.
Intento 1 de 3 falló. Reintentando en 2.2s...
Intento 2 de 3 falló. Reintentando en 4.1s...
Operación: 28 tokens, costo estimado: $0.000046 (acumulado: $0.000331)
Respuesta 7: Los flamencos son de color rosado debido a los camarones que comen.
Operación: 27 tokens, costo estimado: $0.000043 (acumulado: $0.000374)
Respuesta 8: Las nutrias marinas se toman de las manos al dormir para no separarse.
Operación: 28 tokens, costo estimado: $0.000046 (acumulado: $0.000420)
Respuesta 9: Las nutrias marinas se toman de las manos mientras duermen para no separarse.
Operación: 27 tokens, costo estimado: $0.000043 (acumulado: $0.000463)
Respuesta 10: Las nutrias marinas se toman de las manos al dormir para no separarse.
Costo total del ensayo: $0.00046
Total tokens del ensayo: 282
```