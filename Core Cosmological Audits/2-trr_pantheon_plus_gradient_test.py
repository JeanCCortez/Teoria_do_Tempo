import pandas as pd
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
from astropy.io import fits
from scipy.optimize import least_squares
import os

# Ajuste para sua pasta de trabalho
os.chdir(r"C:\Users\JM\tese\novos_testes")

def executar_auditoria_pantheon_corrigida(file_name):
    print(f"\n--- INICIANDO AUDITORIA DE ALTA PRECISÃO (TRR): {file_name} ---")
    try:
        # 1. Carregamento
        df = pd.read_csv(file_name, sep=None, engine='python')

        # 2. Mapeamento Estrito
        cols = {c.lower(): c for c in df.columns}
        z_name = cols.get('zcmb') or cols.get('z')
        m_name = cols.get('mu_shoes') or cols.get('mu_pantheon') or cols.get('m_b_corr')
        ra_name = cols.get('ra')
        dec_name = cols.get('dec')
        err_name = cols.get('mu_err') or cols.get('mu_err_shoes')

        if m_name is None:
            raise KeyError("ERRO: Módulo de distância (MU) não encontrado.")

        # 3. Limpeza e Filtro z > 0.02
        df = df.dropna(subset=[z_name, m_name, ra_name, dec_name]).copy()
        df = df[df[z_name] > 0.02].copy()

        z = df[z_name].values.astype(float)
        mu_obs = df[m_name].values.astype(float)
        mu_err = df[err_name].values.astype(float) if err_name else np.ones_like(z) * 0.15

        # 4. Coordenadas Galácticas e Resíduos
        coords = SkyCoord(ra=df[ra_name].values*u.degree, dec=df[dec_name].values*u.degree, frame='icrs')
        l_gal = coords.galactic.l.radian
        b_gal = coords.galactic.b.radian
        
        # Detrending (Isolando a anisotropia)
        residuos = mu_obs - (5 * np.log10(z))
        residuos -= np.mean(residuos)
        
        pesos_norm = 1.0 / mu_err # Peso linear para o least_squares

        # 5. Modelo TRR
        def cost_func(p, l_in, b_in, z_in, res_in, w_in):
            d0, lp, bp = p
            cos_t = np.sin(b_in) * np.sin(bp) + np.cos(b_in) * np.cos(bp) * np.cos(l_in - lp)
            return ((d0 * z_in) * cos_t - res_in) * w_in

        # 6. Ajuste Real (O sinal da TRR)
        print("Calculando Gradiente Anisotrópico Real...")
        x0 = [0.1, np.radians(148), np.radians(-5)]
        res_real = least_squares(cost_func, x0, args=(l_gal, b_gal, z, residuos, pesos_norm), 
                                 bounds=([0, 0, -np.pi/2], [2.0, 2*np.pi, np.pi/2]))
        
        d0_final = res_real.x[0]
        l_final, b_final = np.degrees(res_real.x[1]), np.degrees(res_real.x[2])

        # 7. TESTE MONTE CARLO SHUFFLE (A Prova de Fogo)
        # Embaralhamos os resíduos para ver qual a chance do acaso gerar um D0 como o seu
        print("Iniciando Simulação de Monte Carlo (100 iterações)...")
        blind_d0s = []
        residuos_shuffled = residuos.copy()
        
        for i in range(100):
            np.random.shuffle(residuos_shuffled) # Destrói a correlação espacial
            res_b = least_squares(cost_func, x0, args=(l_gal, b_gal, z, residuos_shuffled, pesos_norm), 
                                 bounds=([0, 0, -np.pi/2], [2.0, 2*np.pi, np.pi/2]))
            blind_d0s.append(res_b.x[0])
            if (i+1) % 20 == 0: print(f"Simulação {i+1}/100 concluída...")

        # 8. Estatísticas Finais
        z_score = (d0_final - np.mean(blind_d0s)) / np.std(blind_d0s)
        
        n = len(z)
        rss_trr = np.sum(res_real.fun**2)
        rss_iso = np.sum((residuos * pesos_norm)**2)
        aic_trr = 2*3 + n * np.log(rss_trr/n)
        aic_iso = 2*0 + n * np.log(rss_iso/n)
        delta_aic = aic_trr - aic_iso

        print("\n" + "="*60)
        print(f"RELATÓRIO DE AUDITORIA FINAL: {file_name}")
        print("="*60)
        print(f"SIGNIFICÂNCIA (SIGMA): {z_score:.2f} σ")
        print(f"DELTA AIC: {delta_aic:.2f}")
        print(f"GRADIENTE D0: {d0_final:.6f}")
        print(f"DIREÇÃO ENCONTRADA: l={l_final:.2f}°, b={b_final:.2f}°")
        print(f"AMOSTRA ÚTIL: {len(z)} Supernovas")
        print("="*60)

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    executar_auditoria_pantheon_corrigida('PantheonPlusSH0ES.csv')