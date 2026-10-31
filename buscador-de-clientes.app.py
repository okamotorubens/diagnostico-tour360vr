def calcular_score_e_auditoria(
    fotos_total,
    tour_360,
    website,
    total_avaliacoes,
    nota,
    has_https=True,
    reivindicada=True,
):
  """Calcula o nível de otimização (saúde da ficha) e os gargalos mapeados."""
  pontos_criticos = []
  oportunidades = []

  # Pontuação base inicial (Perfil 100% Otimizado)
  score_saude = 100

  # 1. Website Oficial & HTTPS (Desconto máx: 20 pts)
  if not website:
    pontos_criticos.append(
        "Sem website oficial vinculado à ficha do Google (perda de tráfego"
        " direto)"
    )
    oportunidades.append(
        "Desenvolvimento de Landing Page / Website Responsivo de alta"
        " conversão"
    )
    score_saude -= 20
  elif not has_https:
    pontos_criticos.append(
        "Website sem certificado de segurança SSL (alerta de site inseguro)"
    )
    oportunidades.append(
        "Adequação de Segurança SSL e Otimização Web Estrutural"
    )
    score_saude -= 10

  # 2. Volume de Avaliações / Prova Social (Desconto: 20 pts)
  if total_avaliacoes < 30:
    pontos_criticos.append(
        f"Volume crítico de avaliações ({total_avaliacoes} total), afetando a"
        " prova social perante concorrentes"
    )
    oportunidades.append(
        "Estratégia Acelerada de Reputação, QR Codes e Gestão de Avaliações no"
        " Google"
    )
    score_saude -= 20

  # 3. Tour Virtual 360° no Google Street View (Desconto: 25 pts)
  if not tour_360:
    pontos_criticos.append(
        "Ausência de Tour Virtual 360° interativo navegável no perfil do Google"
        " Street View"
    )
    oportunidades.append(
        "Implantação de Fotografia 360° Imersiva e Publicação Oficial no Google"
        " Maps"
    )
    score_saude -= 25

  # 4. Acervo e Quantidade de Fotos (Desconto: 15 pts)
  if fotos_total < 8:
    pontos_criticos.append(
        f"Acervo visual reduzido no perfil ({fotos_total} fotos públicas)"
    )
    oportunidades.append(
        "Produção de Fotografia Profissional em Alta Resolução"
    )
    score_saude -= 15

  # Piso inteligente: Garante limite entre 20 e 100 para empresas ativas
  score_saude = max(20, min(score_saude, 100))
  score_oportunidade = 100 - score_saude

  return {
      "score_saude": score_saude,
      "score_oportunidade": score_oportunidade,
      "pontos_criticos": pontos_criticos,
      "oportunidades": oportunidades,
  }
