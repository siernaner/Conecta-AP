export default function Sobre() {
    return (
        <div className="container py-5">
            <div className="mx-auto" style={{maxWidth: '850px'}}>
                <h1 className="fw-bold mb-4">Sobre o Projeto</h1>
                
                <div className="card border-0 shadow-sm p-4 p-md-5 bg-white">
                    <h4 className="fw-bold text-primary mb-3">Como nasceu o Conecta Alta Paulista?</h4>
                    <p className="text-muted lh-lg">
                        O projeto nasceu da observação de uma lacuna na comunicação regional. Embora a Alta Paulista possua diversos portais de notícias e sites governamentais, as informações muitas vezes encontram-se dispersas. A ideia foi criar um "nervo central" tecnológico que pudesse monitorar todo o tronco férreo paulista em tempo real.
                    </p>
                    
                    <p className="text-muted lh-lg">
                        Desenvolvido como uma ferramenta de inteligência de dados, o sistema utiliza algoritmos avançados para identificar menções geográficas, garantindo que o morador de cada município tenha acesso ao que realmente importa em sua localidade.
                    </p>

                    <hr className="my-4" />

                    <h4 className="fw-bold text-primary mb-3">Nosso Objetivo</h4>
                    <p className="text-muted lh-lg">
                        O objetivo principal é rastrear, categorizar e centralizar notícias publicadas pelas cidades limítrofes que percorrem a extensão ferroviária entre <strong>Garça e Panorama</strong>. 
                    </p>

                    <div className="bg-light p-4 rounded-3 border-start border-primary border-4 mt-4">
                        <h6 className="fw-bold mb-2">Compromisso com a Região:</h6>
                        <ul className="mb-0 text-muted">
                            <li>Fomento à cidadania e acesso à informação local.</li>
                            <li>Filtragem inteligente para evitar ruídos de notícias de outras regiões.</li>
                            <li>Interface limpa, rápida e acessível para todos os dispositivos.</li>
                            <li>Uso de tecnologia para fortalecer a identidade regional da Alta Paulista.</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}