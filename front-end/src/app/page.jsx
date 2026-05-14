"use client";
import { useEffect, useState } from 'react';
import api from '../services/api';

export default function Home() {
  const [noticias, setNoticias] = useState([]);
  const [carregando_inicial, setCarregandoInicial] = useState(true);
  const [carregando_transicao, setCarregandoTransicao] = useState(false);
  
  const [cidades_disponiveis, setCidadesDisponiveis] = useState([]);
  const [temas_disponiveis, setTemasDisponiveis] = useState([]);

  const [cidade_selecionada, setCidadeSelecionada] = useState('');
  const [tema_selecionado, setTemaSelecionado] = useState('');
  const [data_selecionada, setDataSelecionada] = useState('');

  const [pagina_atual, setPaginaAtual] = useState(1);
  const itens_por_pagina = 15;

  useEffect(() => {
    api.get('/noticias')
      .then(response => {
        const dados = response.data || [];
        setNoticias(dados);
        
        setCidadesDisponiveis([...new Set(dados.map(n => n.cidade).filter(Boolean))].sort());
        setTemasDisponiveis([...new Set(dados.map(n => n.categoria || 'Geral'))].sort());
        setCarregandoInicial(false);
      })
      .catch(() => {
        setCarregandoInicial(false);
      });
  }, []);

  const aplicar_efeito_carregamento = () => {
    setCarregandoTransicao(true);
    setTimeout(() => setCarregandoTransicao(false), 500);
  };

  const mudar_pagina = (numero) => {
    setPaginaAtual(numero);
    aplicar_efeito_carregamento();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handle_filtro_change = (setFiltro, valor) => {
    setFiltro(valor);
    setPaginaAtual(1);
    aplicar_efeito_carregamento();
  };

  const filtrar_por_data = (data_str, filtro) => {
      if (!filtro) return true;
      const data_noticia = new Date(data_str);
      const hoje = new Date();
      const diff_dias = Math.ceil(Math.abs(hoje - data_noticia) / (1000 * 60 * 60 * 24));
      if (filtro === 'hoje') return diff_dias <= 1;
      if (filtro === '3_dias') return diff_dias <= 3;
      if (filtro === '7_dias') return diff_dias <= 7;
      return true;
  };

  const noticias_filtradas = noticias.filter(n => {
      const match_cidade = cidade_selecionada ? n.cidade === cidade_selecionada : true;
      const match_tema = tema_selecionado ? (n.categoria || 'Geral') === tema_selecionado : true;
      const match_data = filtrar_por_data(n.data_publicacao, data_selecionada);
      return match_cidade && match_tema && match_data;
  });

  const total_paginas = Math.ceil(noticias_filtradas.length / itens_por_pagina);
  const inicio = (pagina_atual - 1) * itens_por_pagina;
  const itens_exibidos = noticias_filtradas.slice(inicio, inicio + itens_por_pagina);

  return (
    <div className="mt-2">
      <div className="card shadow-sm border-0 mb-4 bg-white">
          <div className="card-body p-4">
              <h5 className="fw-bold mb-3"><i className="bi bi-funnel-fill text-primary me-2"></i>Filtros</h5>
              <div className="row g-3">
                  <div className="col-md-4">
                      <select className="form-select" value={cidade_selecionada} onChange={(e) => handle_filtro_change(setCidadeSelecionada, e.target.value)}>
                          <option value="">Todas as Cidades</option>
                          {cidades_disponiveis.map(c => <option key={c} value={c}>{c}</option>)}
                      </select>
                  </div>
                  <div className="col-md-4">
                      <select className="form-select" value={tema_selecionado} onChange={(e) => handle_filtro_change(setTemaSelecionado, e.target.value)}>
                          <option value="">Todos os Temas</option>
                          {temas_disponiveis.map(t => <option key={t} value={t}>{t}</option>)}
                      </select>
                  </div>
                  <div className="col-md-4">
                      <select className="form-select" value={data_selecionada} onChange={(e) => handle_filtro_change(setDataSelecionada, e.target.value)}>
                          <option value="">Qualquer Data</option>
                          <option value="hoje">Últimas 24h</option>
                          <option value="3_dias">Últimos 3 dias</option>
                          <option value="7_dias">Última semana</option>
                      </select>
                  </div>
              </div>
          </div>
      </div>

      <div className="d-flex justify-content-between align-items-center mb-4">
          <h2 className="fw-bold m-0">Feed Regional</h2>
          {noticias_filtradas.length > 0 && (
              <span className="badge bg-secondary">{noticias_filtradas.length} resultados</span>
          )}
      </div>

      {carregando_inicial || carregando_transicao ? (
        <div className="text-center py-5">
            <div className="spinner-border text-primary" role="status"></div>
            <p className="text-muted mt-2 small">Atualizando feed...</p>
        </div>
      ) : itens_exibidos.length === 0 ? (
        <div className="alert alert-info text-center">Nenhum dado encontrado para os filtros aplicados.</div>
      ) : (
        <>
            <div className="row g-4">
              {itens_exibidos.map((noticia) => (
                <div key={noticia.id} className="col-md-6 col-lg-4">
                  <div className="card h-100 shadow-sm border-0 border-top border-primary border-3 d-flex flex-column">
                    <div className="card-body d-flex flex-column pb-2">
                      <div className="mb-2">
                          <span className="badge bg-primary-subtle text-primary border border-primary-subtle me-1">{noticia.categoria || 'Geral'}</span>
                      </div>
                      
                      {/* Título travado em 3 linhas com minHeight para manter o card do mesmo tamanho */}
                      <h5 className="card-title fw-bold" style={{ 
                          fontSize: '1rem', 
                          lineHeight: '1.4',
                          minHeight: '4.2rem', // 1.4rem * 3 linhas
                          display: '-webkit-box', 
                          WebkitLineClamp: '3', 
                          WebkitBoxOrient: 'vertical', 
                          overflow: 'hidden'
                      }}>
                          {noticia.titulo}
                      </h5>
                      
                      {/* Resumo travado em exatamente 3 linhas com reticências */}
                      <p className="card-text text-muted small mb-0 mt-2" style={{ 
                          display: '-webkit-box', 
                          WebkitLineClamp: '3', 
                          WebkitBoxOrient: 'vertical', 
                          overflow: 'hidden',
                          minHeight: '3.8rem' // Espaço equivalente a 3 linhas para alinhar todos
                      }}>
                          {noticia.resumo}
                      </p>
                    </div>
                    
                    <div className="card-footer bg-white border-top pt-3 pb-3 mt-auto">
                      <div className="d-flex justify-content-between align-items-end">
                          <div className="d-flex flex-column gap-1 text-start">
                              <small className="text-dark fw-bold" style={{ fontSize: '0.75rem' }}>
                                  <i className="bi bi-calendar3 me-1"></i>
                                  {new Date(noticia.data_publicacao).toLocaleDateString('pt-BR')}
                              </small>
                              <div>
                                  <span className="badge bg-info-subtle text-info-emphasis border border-info-subtle" style={{ fontSize: '0.7rem' }}>
                                      <i className="bi bi-geo-alt-fill me-1"></i>{noticia.cidade || 'Região'}
                                  </span>
                              </div>
                              <small className="text-muted fst-italic mt-1" style={{ fontSize: '0.7rem' }}>
                                  <strong>Fonte:</strong> {noticia.fonte_nome || 'Portal de Notícias'}
                              </small>
                          </div>
                          
                          {/* Botão original restaurado */}
                          <a href={noticia.url_original} target="_blank" rel="noopener noreferrer" className="btn btn-outline-primary btn-sm px-3 rounded-pill">
                            Ver Matéria Completa <i className="bi bi-arrow-up-right small ms-1"></i>
                          </a>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {total_paginas > 1 && (
                <nav className="d-flex justify-content-center mt-5 mb-4">
                    <ul className="pagination pagination-sm shadow-sm">
                        <li className={`page-item ${pagina_atual === 1 ? 'disabled' : ''}`}>
                            <button className="page-link" onClick={() => mudar_pagina(pagina_atual - 1)}>Anterior</button>
                        </li>
                        {Array.from({ length: total_paginas }, (_, i) => (
                            <li key={i+1} className={`page-item ${pagina_atual === i+1 ? 'active' : ''}`}>
                                <button className="page-link" onClick={() => mudar_pagina(i+1)}>{i+1}</button>
                            </li>
                        ))}
                        <li className={`page-item ${pagina_atual === total_paginas ? 'disabled' : ''}`}>
                            <button className="page-link" onClick={() => mudar_pagina(pagina_atual + 1)}>Próxima</button>
                        </li>
                    </ul>
                </nav>
            )}
        </>
      )}
    </div>
  );
}