"use client";
import { useEffect, useState, useContext } from 'react';
import api from '../services/api';
import { AuthContext } from '../contexts/AuthContext';

export default function Home() {
  const { user, setUser } = useContext(AuthContext);
  const [noticias, setNoticias] = useState([]);
  const [carregando, setCarregando] = useState(true);
  
  const [mostrarModal, setMostrarModal] = useState(false);
  const [temasDisponiveis, setTemasDisponiveis] = useState([]);
  const [temasSelecionados, setTemasSelecionados] = useState([]);

  useEffect(() => {
    api.get('/noticias')
      .then(response => {
        const data = response.data;
        setNoticias(data);
        setCarregando(false);
        
        const categoriasUnicas = [...new Set(data.map(n => n.categoria || 'Notícias Gerais'))];
        setTemasDisponiveis(categoriasUnicas);
        
        if (user) {
            if (user.preferencias === null || user.preferencias === '') {
                setTemasSelecionados(categoriasUnicas);
                setMostrarModal(true);
            } else {
                setTemasSelecionados(user.preferencias.split(','));
            }
        }
      })
      .catch(error => {
        setCarregando(false);
      });
  }, [user]);

  const salvar_preferencias = async () => {
      try {
          await api.post('/preferencias', { temas: temasSelecionados });
          const preferencias_str = temasSelecionados.join(',');
          localStorage.setItem('preferencias', preferencias_str);
          setUser({ ...user, preferencias: preferencias_str });
          setMostrarModal(false);
      } catch (e) {
          alert("Erro ao salvar preferências.");
      }
  };

  const toggle_tema = (tema) => {
      if (temasSelecionados.includes(tema)) {
          setTemasSelecionados(temasSelecionados.filter(t => t !== tema));
      } else {
          setTemasSelecionados([...temasSelecionados, tema]);
      }
  };

  const noticias_filtradas = noticias.filter(n => {
      if (!user || !user.preferencias) return true;
      return temasSelecionados.includes(n.categoria || 'Notícias Gerais');
  });

  return (
    <div className="mt-4 position-relative">
      <div className="d-flex justify-content-between align-items-center mb-4">
          <h2 className="fw-bold m-0">Feed da Alta Paulista</h2>
          {user && (
              <button 
                onClick={() => setMostrarModal(true)} 
                className="btn btn-outline-secondary btn-sm d-flex align-items-center gap-2"
              >
                <i className="bi bi-gear-fill"></i> Ajustar Temas
              </button>
          )}
      </div>

      {mostrarModal && (
          <div className="modal d-block bg-dark bg-opacity-75" style={{ zIndex: 1050 }}>
              <div className="modal-dialog modal-dialog-centered">
                  <div className="modal-content border-0 shadow-lg">
                      <div className="modal-header bg-primary text-white">
                          <h5 className="modal-title fw-bold">Preferências de Conteúdo</h5>
                          <button type="button" className="btn-close btn-close-white" onClick={() => setMostrarModal(false)}></button>
                      </div>
                      <div className="modal-body">
                          <p className="text-muted small">
                              Selecione os temas que deseja visualizar no seu feed personalizado:
                          </p>
                          <div className="d-flex flex-wrap gap-2 mt-3">
                              {temasDisponiveis.map(tema => (
                                  <div key={tema}>
                                      <input 
                                          type="checkbox" 
                                          className="btn-check" 
                                          id={`btn-check-${tema}`} 
                                          checked={temasSelecionados.includes(tema)}
                                          onChange={() => toggle_tema(tema)}
                                      />
                                      <label className="btn btn-outline-primary btn-sm rounded-pill" htmlFor={`btn-check-${tema}`}>
                                          {temasSelecionados.includes(tema) ? '✓ ' : '+ '} {tema}
                                      </label>
                                  </div>
                              ))}
                          </div>
                      </div>
                      <div className="modal-footer border-0">
                          <button onClick={salvar_preferencias} className="btn btn-primary w-100 fw-bold">
                              Salvar e Atualizar Feed
                          </button>
                      </div>
                  </div>
              </div>
          </div>
      )}

      {carregando ? (
        <div className="text-center mt-5"><div className="spinner-border text-primary"></div></div>
      ) : noticias_filtradas.length === 0 ? (
        <div className="alert alert-warning text-center">
          Nenhuma notícia encontrada para os temas selecionados.
        </div>
      ) : (
        <div className="row g-4">
          {noticias_filtradas.map((noticia) => (
            <div key={noticia.id} className="col-md-6 col-lg-4">
              <div className="card h-100 shadow-sm border-0">
                <div className="card-body">
                  <span className="badge bg-primary mb-2">{noticia.categoria || 'Notícias Gerais'}</span>
                  <h5 className="card-title fw-bold" style={{ fontSize: '1.1rem' }}>{noticia.titulo}</h5>
                  <p className="card-text text-muted" style={{ fontSize: '0.9rem' }}>
                    {noticia.resumo}
                  </p>
                </div>
                <div className="card-footer bg-white border-top-0 d-flex justify-content-between align-items-center">
                  <small className="text-muted">
                    {new Date(noticia.data_publicacao).toLocaleDateString('pt-BR')}
                  </small>
                  <a href={noticia.url_original} target="_blank" rel="noopener noreferrer" className="btn btn-outline-primary btn-sm">
                    Ver Notícia
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}