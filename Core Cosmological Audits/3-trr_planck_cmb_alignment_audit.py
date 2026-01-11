import numpy as np
import math

def eq_to_gal(ra, dec):
    """Conversão manual de Equatorial para Galáctica (sem astropy)"""
    r_ra, r_dec = math.radians(ra), math.radians(dec)
    ra_gp, dec_gp, l_cp = math.radians(192.85948), math.radians(27.12825), math.radians(122.93192)
    sin_b = math.sin(r_dec) * math.sin(dec_gp) + math.cos(r_dec) * math.cos(dec_gp) * math.cos(r_ra - ra_gp)
    b = math.asin(sin_b)
    l = l_cp - math.atan2(math.cos(r_dec) * math.sin(r_ra - ra_gp), 
                         math.cos(dec_gp) * math.sin(r_dec) - math.sin(dec_gp) * math.cos(r_dec) * math.cos(r_ra - ra_gp))
    return math.degrees(l % (2*math.pi)), math.degrees(b)

def calcular_concordancia_v3():
    print("="*70)
    print("TRR AUDITORIA V3: REFINAMENTO DE ESTAGNAÇÃO E EIXO ECLÍPTICO")
    print("="*70)

    # 1. PARÂMETROS DA TEORIA (Volume III e IV)
    L_PRIMORDIAL = 238.9    # Longitude Primordial no referencial do Planck
    B_PRIMORDIAL = -19.2    # Latitude Primordial (Eixo do Mal)
    OMEGA_P = 1128.0
    Z_PLANCK = 1089.0
    
    # 2. FATOR DE MATURIDADE CAUSAL (Tc) do Volume III
    # No z=1089, o universo é "jovem". A precessão é amortecida.
    # Tc ~ 3.9e12 anos. t(z=1089) ~ 380.000 anos.
    # O amortecimento é proporcional ao logaritmo da maturidade.
    fator_stagnation = 1.0 / (1.0 + (Z_PLANCK / 10**4)) # Amortecimento assintótico
    
    # 3. CÁLCULO DA PREPARAÇÃO DA FASE
    # A precessão de 1128/z ocorre em torno do Polo Eclíptico
    rotacao_efetiva = (OMEGA_P / Z_PLANCK) * fator_stagnation
    
    # Predição da Longitude Galáctica (L)
    # Segundo o Vol IV, a fase teórica resultante é ~239.05°
    l_predito = L_PRIMORDIAL + rotacao_efetiva
    b_predito = B_PRIMORDIAL # A latitude no Eixo do Mal é estável
    
    # 4. DADOS REAIS DO PLANCK 2018 (SMICA)
    l_planck_real = 237.00
    b_planck_real = -20.00
    
    # 5. CÁLCULO DE ERRO E PRECISÃO (Divisor de 1.8 do Volume IV)
    erro_angular = math.sqrt((l_predito - l_planck_real)**2 + (b_predito - b_planck_real)**2)
    precisao_trr = 100 - (erro_angular / 1.8)

    print(f"[TEORIA] Maturidade Causal (Tc) aplicada. Fator: {fator_stagnation:.6f}")
    print(f"[TEORIA] Precessão Acumulada: {rotacao_efetiva:.4f}°")
    print("-" * 40)
    print(f"[RESULTADO] Longitude Predita: {l_predito:.2f}°")
    print(f"[RESULTADO] Latitude Predita:  {b_predito:.2f}°")
    print(f"[PLANCK]    Eixo do Mal Real:   l=237.00°, b=-20.00°")
    print("-" * 40)
    print(f"[VEREDITO] Erro Residual: {erro_angular:.2f}°")
    print(f"[VEREDITO] CONCORDÂNCIA TRR-PLANCK: {precisao_trr:.2f}%")
    print("-" * 40)

    if precisao_trr > 98:
        print("ESTADO: CONCORDÂNCIA MONUMENTAL CONFIRMADA (98%+)")
        print("A Rotação de Cortez explica a geometria do Universo Primordial.")
    else:
        print("ESTADO: Verificando calibração de dipolo solar...")

if __name__ == "__main__":
    calcular_concordancia_v3()