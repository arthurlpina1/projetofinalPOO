def ler_horario(mensagem):
    # lê "hh:mm" e devolve o total de minutos desde 00:00
    while True:
        texto = input(mensagem).strip()
        partes = texto.split(":")

        if len(partes) == 2 and partes[0].isdigit() and partes[1].isdigit():
            horas = int(partes[0])
            minutos = int(partes[1])
            if horas < 24 and minutos < 60:
                return horas * 60 + minutos

        print("Horário inválido. Use o formato hh:mm (ex.: 08:30).")


def formatar_horario(total_minutos):
    horas = total_minutos // 60
    minutos = total_minutos % 60
    return f"{horas:02d}:{minutos:02d}"


class Veiculo:
    def __init__(self, placa, horario_entrada):
        self.placa = placa
        self.horario_entrada = horario_entrada   # em minutos
        self.horario_saida = 0                   # em minutos
        self.tipo = ""
        self.tipo_vaga = ""                      # tipo da vaga onde está estacionado
        self.preco_hora_tipo = 0

    def calcular_preco(self):
        minutos = self.horario_saida - self.horario_entrada
        return minutos / 60 * self.preco_hora_tipo

class Carro(Veiculo):
    def __init__(self, placa, horario_entrada):
        super().__init__(placa, horario_entrada)
        self.tipo = "carro"
        self.preco_hora_tipo = 10

class Moto(Veiculo):
    def __init__(self, placa, horario_entrada):
        super().__init__(placa, horario_entrada)
        self.tipo = "moto"
        self.preco_hora_tipo = 5

class Estacionamento:
    def __init__(self, ordem_matriz):
        self.ordem_matriz = ordem_matriz
        self.vagas = []
        for i in range(ordem_matriz):
            linha = []
            for j in range(ordem_matriz):
                if self.ordem_matriz == 2:
                    if i == 0:
                        linha.append("carro")
                    else:
                        linha.append("moto")

                elif i < (self.ordem_matriz // 2) + 1:
                    linha.append("carro")
                else:
                    linha.append("moto")
            self.vagas.append(linha)
        self.faturamento = 0
        self.vagas_carro = 0
        self.vagas_moto = 0
        self.permanencias = []   # em minutos

    # ---------- funções auxiliares ----------

    def vaga_livre(self, i, j):
        vaga = self.vagas[i][j]
        return vaga == "carro" or vaga == "moto"   #se n tiver veiculo estacionado retorna verdadeiro

    def vagas_livres(self, tipo):
        total = 0
        for i in range(self.ordem_matriz):
            for j in range(self.ordem_matriz):
                if self.vagas[i][j] == tipo:   # vaga livre guarda o próprio tipo
                    total += 1
        return total

    def vaga_mais_proxima(self, tipo):
        for i in range(self.ordem_matriz):
            for j in range(self.ordem_matriz):
                if self.vagas[i][j] == tipo:
                    return i, j
        return None

    def escolher_vaga(self, tipo):
        while True:
            i = int(input("Linha da vaga: ")) - 1
            j = int(input("Coluna da vaga: ")) - 1

            if i < 0 or i >= self.ordem_matriz or j < 0 or j >= self.ordem_matriz:
                print("Essa vaga não existe. Tente de novo.")
            elif not self.vaga_livre(i, j):
                print("Essa vaga está ocupada. Tente de novo.")
            elif self.vagas[i][j] != tipo:
                print(f"Essa vaga não é de {tipo}. Tente de novo.")
            else:
                return i, j

    def buscar(self, placa):
        # devolve (linha, coluna) do veículo, ou None se não achar
        for i in range(self.ordem_matriz):
            for j in range(self.ordem_matriz):
                if not self.vaga_livre(i, j) and self.vagas[i][j].placa == placa:
                    return i, j
        return None

    # ---------- opções do menu ----------

    def registrar_entrada(self):
        tipo = input("Tipo (carro/moto): ").lower()
        if tipo != "carro" and tipo != "moto":
            print("Tipo inválido.")
            return

        placa = input("Placa: ").upper()
        if self.buscar(placa) is not None:
            print("Esse veículo já está estacionado.")
            return

        entrada = ler_horario("Horário de entrada (hh:mm): ")

        if tipo == "carro":
            veiculo = Carro(placa, entrada)
        else:
            veiculo = Moto(placa, entrada)

        tipo_vaga = veiculo.tipo

        # se não tem vaga do tipo certo
        if self.vagas_livres(tipo_vaga) == 0:
            if tipo_vaga == "moto" and self.vagas_livres("carro") > 0:
                resp = input("Sem vaga de moto. Pagar mais caro e usar vaga de carro? (s/n): ").lower()
                if resp != "s":
                    print("Aguarde uma vaga de moto ser liberada.")
                    return
                tipo_vaga = "carro"
                veiculo.preco_hora_tipo = 10  # a moto paga como carro
            else:
                print(f"Sem vagas de {tipo_vaga}. Aguarde uma vaga ser liberada.")
                return

        print(f"Vagas de {tipo_vaga} livres: {self.vagas_livres(tipo_vaga)}")

        # escolher a vaga
        resp = input("Escolher a vaga? (s/n): ")
        if resp == "s":
            i, j = self.escolher_vaga(tipo_vaga)
        else:
            i, j = self.vaga_mais_proxima(tipo_vaga)

        veiculo.tipo_vaga = tipo_vaga   # guarda o tipo da vaga para liberar na saída
        self.vagas[i][j] = veiculo

        if veiculo.tipo == "carro":
            self.vagas_carro += 1
        else:
            self.vagas_moto += 1

        print(f"Estacionado na linha {i + 1}, coluna {j + 1}.")

    def registrar_saida(self):
        placa = input("Placa: ").upper()
        posicao = self.buscar(placa)

        if posicao is None:
            print("Veículo não encontrado.")
            return

        i, j = posicao
        veiculo = self.vagas[i][j]
        saida = ler_horario("Horário de saída (hh:mm): ")

        if saida < veiculo.horario_entrada:
            saida = saida + 24 * 60   # saiu no dia seguinte

        veiculo.horario_saida = saida
        permanencia = saida - veiculo.horario_entrada

        valor = veiculo.calcular_preco()
        self.faturamento += valor
        self.permanencias.append(permanencia)
        self.vagas[i][j] = veiculo.tipo_vaga  # a vaga volta a ser "carro" ou "moto"

        print(f"Permanência: {formatar_horario(permanencia)}")
        print(f"Valor a pagar: R$ {valor:.2f}")


    def mostrar_estacionamento(self):
        for i in range(self.ordem_matriz):
            texto = ""
            for j in range(self.ordem_matriz):
                if self.vaga_livre(i, j):
                    texto += f"[{self.vagas[i][j]}]".ljust(10)
                else:
                    texto += self.vagas[i][j].placa.ljust(10)
            print(texto)

    def listar_estacionados(self):
        achou = False
        for i in range(self.ordem_matriz):
            for j in range(self.ordem_matriz):
                if not self.vaga_livre(i, j):
                    veiculo = self.vagas[i][j]
                    print(veiculo.tipo, veiculo.placa, "- entrada:", formatar_horario(veiculo.horario_entrada))
                    achou = True
        if not achou:
            print("Nenhum veículo estacionado.")


    def buscar_placa(self):
        placa = input("Placa: ").upper()
        posicao = self.buscar(placa)

        if posicao is None:
            print("Veículo não encontrado.")
        else:
            i, j = posicao
            print(f"Linha {i + 1}, coluna {j + 1}")

    def alterar_veiculo(self):
        placa = input("Placa do veículo: ").upper()
        posicao = self.buscar(placa)

        if posicao is None:
            print("Veículo não encontrado.")
            return

        i, j = posicao
        veiculo = self.vagas[i][j]
        print("1 - Alterar placa")
        print("2 - Alterar horário de entrada")
        print("0 - Cancelar")
        opcao = int(input("Opção: "))

        if opcao == 1:
            nova_placa = input("Nova placa: ").upper()
            if self.buscar(nova_placa) is not None:
                print("Já existe um veículo com essa placa.")
            else:
                veiculo.placa = nova_placa
                print("Placa alterada.")
        elif opcao == 2:
            novo_horario = ler_horario("Novo horário de entrada (hh:mm): ")
            veiculo.horario_entrada = novo_horario
            print("Horário alterado para", formatar_horario(novo_horario))
        elif opcao == 0:
            print("Alteração cancelada.")
        else:
            print("Opção inválida.")

    def mostrar_estatisticas(self):
        total = self.vagas_carro + self.vagas_moto

        if total > 0:
            percentual_carros = self.vagas_carro / total * 100
            percentual_motos = self.vagas_moto / total * 100
            print("Carros:", round(percentual_carros, 1), "%")
            print("Motos:", round(percentual_motos, 1), "%")

        if len(self.permanencias) > 0:
            media = sum(self.permanencias) / len(self.permanencias)
            print("Permanência média:", formatar_horario(round(media)))

        print(f"Faturamento: R$ {self.faturamento:.2f}")


ordem = int(input("ordem da matriz: "))
est = Estacionamento(ordem)
est.mostrar_estacionamento()

while True:
    print()
    print("1 - Entrada")
    print("2 - Saída")
    print("3 - Mostrar estacionamento")
    print("4 - Listar estacionados")
    print("5 - Buscar placa")
    print("6 - Consultar vagas")
    print("7 - Estatísticas")
    print("8 - Alterar veículo")
    print("0 - Encerrar")
    opcao = int(input("Opção: "))

    if opcao == 1:
        est.registrar_entrada()
    elif opcao == 2:
        est.registrar_saida()
    elif opcao == 3:
        est.mostrar_estacionamento()
    elif opcao == 4:
        est.listar_estacionados()
    elif opcao == 5:
        est.buscar_placa()
    elif opcao == 6:
        print("Vagas de carro:", est.vagas_livres("carro"))
        print("Vagas de moto:", est.vagas_livres("moto"))
    elif opcao == 7:
        est.mostrar_estatisticas()
    elif opcao == 8:
        est.alterar_veiculo()
    elif opcao == 0:
        break
    else:
        print("Escolha uma opção válida")

print()
print("--- RESUMO FINAL ---")
est.mostrar_estatisticas()