"use client";
import { useEffect, useState, useRef, useContext } from 'react';
import api from '../services/api';
import { AuthContext } from '../contexts/AuthContext';

export default function Home() {
  const { user } = useContext(AuthContext);
  const [noticias, setNoticias] = useState([]);
  const [carregando_inicial, setCarregandoInicial] = useState(true);
  const [carregando_transicao, setCarregandoTransicao] = useState(false);
  const [carregando_mais, setCarregandoMais] = useState(false);
  
  const [cidades_disponiveis, setCidadesDisponiveis] = useState([]);
  const [temas_disponiveis, setTemasDisponiveis] = useState([]);

  const [cidade_selecionada, setCidadeSelecionada] = useState('');
  const [tema_selecionado, setTemaSelecionado] = useState('');
  const [data_selecionada, setDataSelecionada] = useState('');
  
  const [busca, setBusca] = useState('');
  const [busca_debounced, setBuscaDebounced] = useState('');

  const [itens_visiveis, setItensVisiveis] = useState(15);
  const observer = useRef();
  const [showScrollTop, setShowScrollTop] = useState(false);
  const idsMarcados = useRef(new Set()); // evitar marcar duplicado

  const obterIdUsuario = () => {
    if (user && user.id) return user.id;
    return null;
  };

  // Salvar posição de rolagem antes de recarregar
  useEffect(() => {
    const handleBeforeUnload = () => {
      sessionStorage.setItem('scrollPosition', window.scrollY);
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, []);

  // Restaurar posição após carregar
  useEffect(() => {
    const savedScroll = sessionStorage.getItem('scrollPosition');
    if (savedScroll) {
      window.scrollTo(0, parseInt(savedScroll));
      sessionStorage.removeItem('scrollPosition');
    }
  }, []);

  // Mostrar botão de topo
  useEffect(() => {
    const handleScroll = () => setShowScrollTop(window.scrollY > 500);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' });

  // Debounce da busca
  useEffect(() => {
    const timer = setTimeout(() => {
      setBuscaDebounced(busca);
      setItensVisiveis(15);
    }, 1000);
    return () => clearTimeout(timer);
  }, [busca]);

  // Carregar notícias
  useEffect(() => {
    const u_id = obterIdUsuario() || '';
    api.get(`/noticias?u_id=${u_id}&t=${Date.now()}`)
      .then(response => {
        const dados = response.data || [];
        const processadas = dados.map(n => ({
            ...n,
            status_leitura: u_id ? n.status_leitura : null 
        }));
        setNoticias(processadas);
        setCidadesDisponiveis([...new Set(dados.map(n => n.cidade).filter(Boolean))].sort());
        setTemasDisponiveis([...new Set(dados.map(n => n.categoria || 'Geral'))].sort());
        setCarregandoInicial(false);
      })
      .catch(() => setCarregandoInicial(false));
  }, [user]);

  // Marcar como vista quando o card fica visível por 1 segundo
  useEffect(() => {
    if (!user) return;
    const observerVista = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = parseInt(entry.target.dataset.id);
          if (!idsMarcados.current.has(id)) {
            const timer = setTimeout(() => {
              if (entry.isIntersecting) {
                marcarComoVista(id);
                idsMarcados.current.add(id);
              }
            }, 1000);
            entry.target.timer = timer;
          }
        } else {
          if (entry.target.timer) clearTimeout(entry.target.timer);
        }
      });
    }, { threshold: 0.5 });

    const cards = document.querySelectorAll('.noticia-card');
    cards.forEach(card => observerVista.observe(card));
    return () => observerVista.disconnect();
  }, [noticias, user]);

  const marcarComoVista = async (id) => {
    const u_id = obterIdUsuario();
    if (u_id) {
      await api.post('/noticias/marcar-vistas', { ids: [id], u_id }).catch(() => {});
    }
  };

  const aplicar_efeito_carregamento = () => {
    setCarregandoTransicao(true);
    setTimeout(() => setCarregandoTransicao(false), 500);
  };

  const handle_filtro_change = (set_filtro, valor) => {
    set_filtro(valor);
    setItensVisiveis(15);
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
    const termo = busca_debounced.toLowerCase();
    const match_busca = termo ? (
      (n.titulo && n.titulo.toLowerCase().includes(termo)) || 
      (n.resumo && n.resumo.toLowerCase().includes(termo))
    ) : true;
    return match_cidade && match_tema && match_data && match_busca;
  });

  const itens_exibidos = noticias_filtradas.slice(0, itens_visiveis);

  const lastElementRef = (node) => {
    if (carregando_inicial || carregando_transicao || carregando_mais) return;
    if (observer.current) observer.current.disconnect();
    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && itens_visiveis < noticias_filtradas.length) {
        setCarregandoMais(true);
        setTimeout(() => {
          setItensVisiveis(prev => prev + 15);
          setCarregandoMais(false);
        }, 500);
      }
    });
    if (node) observer.current.observe(node);
  };

  const handle_abrir_noticia = (id, url) => {
    const u_id = obterIdUsuario();
    if (u_id) {
      api.post('/noticias/marcar-aberta', { id, u_id }).catch(() => {});
    }
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="mt-2 pb-4">
      <div className="card shadow-sm border-0 mb-4 bg-white">
          <div className="card-body p-4">
              <h5 className="fw-bold mb-3"><i className="bi bi-funnel-fill text-primary me-2"></i>Filtros e Busca</h5>
              <div className="mb-3">
                  <div className="input-group shadow-sm">
                      <span className="input-group-text bg-white border-end-0 text-muted"><i className="bi bi-search"></i></span>
                      <input type="text" className="form-control border-start-0 ps-0" placeholder="Pesquisar..." value={busca} onChange={(e) => setBusca(e.target.value)} />
                  </div>
              </div>
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
          {noticias_filtradas.length > 0 && <span className="badge bg-secondary">{noticias_filtradas.length} resultados</span>}
      </div>

      {carregando_inicial || carregando_transicao ? (
        <div className="text-center py-5"><div className="spinner-border text-primary"></div><p className="text-muted mt-2">Carregando...</p></div>
      ) : itens_exibidos.length === 0 ? (
        <div className="alert alert-info text-center">Nenhuma notícia encontrada.</div>
      ) : (
        <>
          <div className="row g-4">
            {itens_exibidos.map((noticia, index) => (
              <div key={noticia.id} className="col-md-6 col-lg-4 noticia-card" data-id={noticia.id} ref={index === itens_exibidos.length - 1 ? lastElementRef : null}>
                <div className="card h-100 shadow-sm border-0 border-top border-primary border-3">
                  <div className="card-body d-flex flex-column pb-2">
                    <div className="mb-2 d-flex gap-2 align-items-center">
                      <span className="badge bg-primary-subtle text-primary border border-primary-subtle">{noticia.categoria || 'Geral'}</span>
                      {obterIdUsuario() && noticia.status_leitura === 'NOVA' && <span className="badge bg-success">NOVA</span>}
                      {obterIdUsuario() && noticia.status_leitura === 'VISTA' && <span className="badge" style={{ backgroundColor: '#c8e6c9', color: '#1b5e20' }}>VISTA</span>}
                      {obterIdUsuario() && noticia.status_leitura === 'ABERTA' && <span className="badge bg-secondary text-white">ABERTA</span>}
                    </div>
                    <h5 className="card-title fw-bold" style={{ fontSize: '1rem', lineHeight: '1.4', minHeight: '4.2rem', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                      {noticia.titulo}
                    </h5>
                    <p className="card-text text-muted small mb-0 mt-2" style={{ WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden', minHeight: '3.8rem' }}>
                      {noticia.resumo}
                    </p>
                  </div>
                  <div className="card-footer bg-white border-top pt-3 pb-3">
                    <div className="d-flex justify-content-between align-items-end">
                      <div className="d-flex flex-column gap-1">
                        <small className="text-dark fw-bold"><i className="bi bi-calendar3 me-1"></i>Publicado: {new Date(noticia.data_publicacao).toLocaleDateString('pt-BR')}</small>
                        <small className="text-dark fw-bold"><i className="bi bi-clock-history me-1"></i>Importado: {new Date(noticia.data_importacao || noticia.data_publicacao).toLocaleDateString('pt-BR')}</small>
                        <div><span className="badge bg-info-subtle text-info-emphasis border border-info-subtle"><i className="bi bi-geo-alt-fill me-1"></i>{noticia.cidade || 'Região'}</span></div>
                        <small className="text-muted fst-italic"><strong>Fonte:</strong> {noticia.fonte_nome || 'Portal'}</small>
                      </div>
                      <button onClick={() => handle_abrir_noticia(noticia.id, noticia.url_original)} className="btn btn-outline-primary btn-sm px-3 rounded-pill">Ver Matéria <i className="bi bi-arrow-up-right small ms-1"></i></button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          {carregando_mais && <div className="text-center mt-4"><div className="spinner-border text-primary spinner-border-sm"></div><span className="ms-2 text-muted">Carregando...</span></div>}
        </>
      )}
      {showScrollTop && (
        <button onClick={scrollToTop} className="btn btn-primary rounded-circle position-fixed" style={{ bottom: '20px', right: '20px', zIndex: 1000, width: '50px', height: '50px' }}>
          <i className="bi bi-arrow-up"></i>
        </button>
      )}
    </div>
  );
}