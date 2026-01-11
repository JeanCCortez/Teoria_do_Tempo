import pandas as pd
import numpy as np
import os

# CONFIGURAÇÃO DE RIGOR MÁXIMO (SEM PARÂMETROS LIVRES)
PASTA_DADOS = r'C:\Users\JM\tese\novos_testes\Rotmod_LTG'
A0_FIXO = 1.2e-10  # A constante da TRR
ML_ESTRITO = 0.5   # O valor físico real medido pelo Spitzer

def lei_de_cortez_pura(rad, v_gas, v_disk, v_bul):
    # Cálculo barônico sem qualquer ajuste artificial
    v_bar_sq = v_gas**2 + (v_disk**2 * ML_ESTRITO) + (v_bul**2 * 0.7)
    r_meters = rad * 3.086e19
    
    if r_meters <= 0 or v_bar_sq <= 0: return 0
    
    g_bar = (v_bar_sq * 1000**2) / r_meters
    
    # A equação fundamental da TRR (sem simplificações)
    # g_total = g_bar / (1 - exp(-sqrt(g_bar / a0)))
    g_total = g_bar / (1 - np.exp(-np.sqrt(g_bar / A0_FIXO)))
    
    return np.sqrt(g_total * r_meters) / 1000

def auditoria_estrita():
    print("--- TRR: AUDITORIA DE RIGOR ABSOLUTO (SEM AJUSTES AD HOC) ---")
    arquivos = [f for f in os.listdir(PASTA_DADOS) if f.endswith('.dat')]
    log_erros = []

    for arquivo in arquivos:
        try:
            df = pd.read_csv(os.path.join(PASTA_DADOS, arquivo), sep=r'\s+', comment='#', header=None,
                             names=['Rad', 'Vobs', 'errV', 'Vgas', 'Vdisk', 'Vbul', 'SBdis', 'SBbul'])
            df = df.apply(pd.to_numeric, errors='coerce').dropna(subset=['Vobs'])
            
            # Pegamos apenas os dados da borda (onde a Matéria Escura supostamente domina)
            # É aqui que a TRR tem que provar seu valor
            df_borda = df[df['Rad'] > df['Rad'].max() * 0.8] 

            v_trr = df_borda.apply(lambda x: lei_de_cortez_pura(x['Rad'], x['Vgas'], x['Vdisk'], x['Vbul']), axis=1)
            erro = np.mean(v_trr - df_borda['Vobs']) # Diferença real em km/s
            log_erros.append(erro)
        except: continue

    media_residuo = np.mean(log_erros)
    desvio_padrao = np.std(log_erros)

    print(f"\nResíduo Médio de Velocidade: {media_residuo:.2f} km/s")
    print(f"Desvio Padrão (Fidelidade da Lei): {desvio_padrao:.2f} km/s")
    print("-" * 50)
    print("INTERPRETAÇÃO TÉCNICA:")
    if abs(media_residuo) < 10:
        print("[SUCESSO] A lei de Cortez crava a velocidade sem massa invisível.")
    else:
        print("[VIÉS] Existe um desvio sistemático que sugere calibração de escala.")

if __name__ == "__main__":
    auditoria_estrita()