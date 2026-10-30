import re
import random
import tkinter as tk

BG, PANEL, AMBER, TEAL, RED, FG, DIM = "#0b0d10", "#12100c", "#ffb347", "#5ee0d0", "#ff4d5e", "#e8dcc6", "#7a6a50"
SERIF = ("Georgia", 14)
MONO = ("Consolas", 10)

CLUES = {
    "watch":   ("Часы", "Остановились, когда поезд вошёл в Ночь. Время здесь не твой союзник."),
    "ticket":  ("Билет", "Билет без станции назначения. Название стёрто чернилами."),
    "photo":   ("Фото", "Ты уже был в этом купе. Значит, ты здесь не впервые."),
    "ash":     ("Пепел", "Это не еда. Так выглядят выжженные воспоминания."),
    "key":     ("Ключ", "Ключ машиниста от кабины и стоп-крана."),
    "log":     ("Бортжурнал", "«Меридиан» идёт по кругу. Двигатель питается памятью пассажиров."),
    "ampoule": ("Ампула «Лета»", "Пустая ампула. Такой стирали память. Тебе тоже."),
}
NAMES = {"tessa": "Тесса", "auer": "Ауэр", "leo": "Лео"}


def has(*items):
    return lambda s: all(i in s.inv for i in items)


class State:
    def __init__(self):
        self.san = 100
        self.time = 12
        self.tr = {"tessa": 0, "auer": 0, "leo": 0}
        self.inv = []
        self.f = {}
        self.done = set()


SC = {
    "start": dict(
        loc="КУПЕ №7",
        t="Тебя будит не гудок, а тишина. «Пезд» идёт сквозь Вечную Ночь уже [[watch|четыре тысячи дней]], "
          "и каждое утро ты не помнишь вчерашнего.\n\n"
          "На столике лежит [[ticket|билет]] без станции назначения. В кармане [[photo|фотография]]: "
          "ты в этом же купе. На обороте твоим почерком: «НЕ ВЕРЬ ПРОВОДНИЦЕ».",
        msg="БЮРО РАССВЕТА: Ревизор, машинист Корвин мёртв. До станции Зарево 12 перегонов. "
            "Найдите убийцу, иначе поезд не остановится.",
        ch=[dict(x="Выйти в коридор", to="hub", time=-1)]),

    "hub": dict(
        loc="КОРИДОР",
        t="Коридор тянется сквозь вагоны, лампы мигают в такт колёсам. За окнами нет ничего, даже темноты, "
          "только отражение твоего лица, которое смотрит чуть дольше, чем должно.\n\n"
          "Из вагона-ресторана тянет холодом. У купе проводницы горит свет. Где-то в радиорубке трещит эфир. "
          "Дверь с табличкой «КАБИНА» заперта.",
        ch=[dict(x="Вагон-ресторан (тело Корвина)", to="body", time=-1),
            dict(x="Поговорить с Тессой, проводницей", to="tessa", time=-1),
            dict(x="Зайти к доктору Ауэру", to="auer", time=-1),
            dict(x="Заглянуть в радиорубку к Лео", to="leo", time=-1),
            dict(x="Открыть кабину машиниста", to="engine", time=-1, req=has("key"), lock="Нужен ключ машиниста")]),

    "body": dict(
        loc="ВАГОН-РЕСТОРАН",
        t="Корвин сидит за накрытым столом, словно уснул. В тарелке вместо еды лежит серый [[ash|пепел]]. "
          "На шее у него цепочка, в сжатой ладони блестит [[key|ключ]].\n\n"
          "Глаза открыты. В зрачках отражается не вагон, а залитая солнцем платформа. Ты никогда не видел солнца.",
        ch=[dict(x="Разжать мёртвые пальцы и взять ключ", to="body", san=-8, add=["key"], once="key", shake=True),
            dict(x="Вернуться в коридор", to="hub", time=-1)]),

    "tessa": dict(
        loc="КУПЕ ПРОВОДНИЦЫ",
        t="Тесса Марр поправляет форменный воротничок. Улыбка идеальна, как у фарфоровой куклы.\n\n"
          "— Ревизор. Вы очень бледны. Вчера вы спрашивали то же самое. И позавчера.\n\n"
          "Она говорит спокойно, но пальцы нервно крутят пуговицу, и это единственное живое в ней.",
        ch=[dict(x="Показать фотографию с надписью", to="tessa2", req=has("photo"), lock="Нет фотографии", time=-1),
            dict(x="«Ты лгала мне. Что ты скрываешь?»", to="tessa_bad", tr={"tessa": -2}, san=-5, time=-1),
            dict(x="Уйти", to="hub")]),

    "tessa2": dict(
        loc="КУПЕ ПРОВОДНИЦЫ",
        t="Улыбка гаснет. Тесса долго смотрит на надпись.\n\n"
          "— Это писал не ревизор. Это писал тот, кого мы убили. Вернее, тот, кто убил... Простите. "
          "Меня стирают каждую ночь, я автомат. Но Корвин оставил в моей памяти одну вещь.\n\n"
          "Она протягивает потёртый [[log|бортжурнал]].\n\n"
          "— Он просил остановить поезд. Мне это запрещено. Вам нет.",
        ch=[dict(x="Взять журнал и поблагодарить", to="hub", tr={"tessa": 2}, san=-5, add=["log"], time=-1)]),

    "tessa_bad": dict(
        loc="КУПЕ ПРОВОДНИЦЫ",
        t="Лампа вспыхивает красным. Тесса выпрямляется, и в голосе исчезает всё человеческое.\n\n"
          "— Протокол «Допрос» не предусмотрен. Прошу вернуться в купе.\n\n"
          "Дверь закрывается перед тобой. Через щель слышно, как она тихо повторяет одно слово: "
          "«простите, простите, простите».",
        ch=[dict(x="Вернуться в коридор", to="hub", shake=True)]),

    "auer": dict(
        loc="МЕДВАГОН",
        t="Доктор Ауэр наливает чай в тонкие фарфоровые чашки. Седые виски, мягкий голос.\n\n"
          "— Вы страдаете, Ревизор. Я вижу это по глазам. У меня есть средство, после него ничего не болит. "
          "В саквояже виднеется [[ampoule|пустая ампула]] с надписью «ЛЕТА».\n\n"
          "Он улыбается так, будто давно ждал именно этого разговора.",
        ch=[dict(x="Принять инъекцию: забыть боль", to="auer_lethe", san=25, tr={"auer": 1}, rm=["photo"], time=-1),
            dict(x="Отказаться и сжать чашку", to="auer_no", tr={"auer": -1}, san=-4, time=-1),
            dict(x="Уйти", to="hub")]),

    "auer_lethe": dict(
        loc="МЕДВАГОН",
        t="Холод бежит по венам, и мир становится мягким. Тревога тает, как сахар в чае.\n\n"
          "Позже ты нащупываешь карман. Фотография исчезла. Ты помнишь, что она была, но не помнишь, что на ней.\n\n"
          "Ауэр тихо смеётся: «Вот видите. Совсем не больно».",
        ch=[dict(x="Выйти в коридор", to="hub")]),

    "auer_no": dict(
        loc="МЕДВАГОН",
        t="— Как хотите, — улыбка Ауэра становится тоньше. — Многие отказываются. Первые три раза.\n\n"
          "Ты замечаешь на ампуле штамп цеха двигателя. Зачем врачу запас лекарств для топки?",
        ch=[dict(x="Выйти в коридор", to="hub")]),

    "leo": dict(
        loc="РАДИОРУБКА",
        t="Лео сидит в наушниках на пару размеров больше его головы, перед ним россыпь ламп и тумблеров.\n\n"
          "— Слышите? — шепчет он, не поворачиваясь. — «Зарево, Зарево, говорит Зарево». "
          "Каждую ночь одно и то же слово в слово. Как запись.",
        ch=[dict(x="Отдать ему билет: «Пусть будет твоим»", to="leo_gift", req=has("ticket"), lock="Нет билета",
                 tr={"leo": 2}, rm=["ticket"], time=-1),
            dict(x="Послушать эфир в наушниках", to="leo_radio", san=-10, time=-1, once="radio", tr={"leo": 1}),
            dict(x="Уйти", to="hub")]),

    "leo_gift": dict(
        loc="РАДИОРУБКА",
        t="Лео разглаживает билет ладонью, словно это карта сокровищ.\n\n"
          "— Я никогда не уезжал отсюда, — говорит он. — Знаете, я умею блокировать тормозной привод вручную. "
          "Если надо. Только я один знаю как.",
        ch=[dict(x="Кивнуть и вернуться в коридор", to="hub")]),

    "leo_radio": dict(
        loc="РАДИОРУБКА",
        t="В наушниках детский голос читает название станции. Твоим голосом. Записанным давно.\n\n"
          "Ты срываешь наушники. Лео смотрит с жалостью: «Вы тоже это слышали».",
        ch=[dict(x="Выйти, дрожа", to="hub", shake=True)]),

    "engine": dict(
        loc="КАБИНА МАШИНИСТА", timer=dict(sec=25, to="e_loop"),
        t="Ключ входит в замок как родной. В кабине тепло. Двигатель «Меридиана» не гудит, а шепчет: "
          "тысячи тихих голосов, обрывки чужих детств, свадеб, прощаний.\n\n"
          "За спиной щёлкает дверь. Ауэр держит в руке шприц.\n\n"
          "— Вы нашли ключ, Ревизор. В прошлый раз вы тоже его нашли. Решайте скорее.",
        ch=[dict(x="Предъявить ампулу и фото: «Ты стёр мне память»", to="confront",
                 req=has("ampoule", "photo"), lock="Нужны ампула и фото"),
            dict(x="Рвануть стоп-кран прямо сейчас",
                 to=lambda s: "e_dawn" if (s.f.get("truth") and s.tr["leo"] >= 2 and s.san >= 20) else "e_fail",
                 req=has("log"), lock="Нужен бортжурнал"),
            dict(x="Принять «Лету» из рук Ауэра", to="e_forget")]),

    "confront": dict(
        loc="КАБИНА МАШИНИСТА", timer=dict(sec=25, to="e_loop"),
        enter=lambda s: s.f.__setitem__("truth", 1),
        t="Ауэр долго молчит. Потом опускает шприц.\n\n"
          "— Корвин хотел остановить поезд. Вы, мой друг, убили его моим же ножом, потому что я вам так сказал. "
          "Потом я стёр вам память, чтобы вы смогли сделать это снова.\n\n"
          "Он говорит ласково. Это страшнее крика.\n\n"
          "— Теперь у вас два выхода. Остановить машину и погибнуть вместе с ней. "
          "Или занять место Корвина. Здесь так тепло.",
        ch=[dict(x="Остановить «Меридиан»",
                 to=lambda s: "e_dawn" if (s.tr["leo"] >= 2 and s.san >= 20) else "e_fail",
                 req=has("log"), lock="Нужен бортжурнал"),
            dict(x="Занять место машиниста", to="e_throne"),
            dict(x="Выбросить шприц и закричать", to="e_mad")]),

    "e_dawn": dict(end="КОНЦОВКА: РАССВЕТ",
        t="Ты рвёшь стоп-кран. Лео из радиорубки блокирует привод, как и обещал. Колёса визжат, "
          "и вагоны ползут к остановке.\n\n"
          "Первый луч режет Ночь, как нож. Где-то за стеклом настоящее, невыдуманное солнце. "
          "Пассажиры плачут и вспоминают свои имена.\n\n"
          "Тесса берёт тебя за руку: «Теперь можно помнить вместе»."),
    "e_loop": dict(end="КОНЦОВКА: КРУГ",
        t="Время вышло. «Меридиан» проходит станцию, которой нет.\n\n"
          "Ты просыпаешься в купе №7. На столике билет без станции. В кармане фотография. "
          "На обороте твоим почерком: «НЕ ВЕРЬ ПРОВОДНИЦЕ»."),
    "e_fail": dict(end="КОНЦОВКА: ЗАКЛИНИВШИЙ ТОРМОЗ",
        t="Стоп-кран поддаётся, но привод держит. Без правды и без помощи Лео он не открывается. "
          "Ауэр вздыхает и всаживает иглу в плечо.\n\n«Ничего. Начнём сначала»."),
    "e_mad": dict(end="КОНЦОВКА: БЕЗУМИЕ",
        t="Голоса двигателя выходят из стен. Ты слышишь каждое украденное воспоминание сразу. "
          "Пол, потолок, имя, лицо матери, лицо Корвина, твоё лицо.\n\nТы смеёшься, пока не забываешь, над чем."),
    "e_forget": dict(end="КОНЦОВКА: ЗАБВЕНИЕ",
        t="Игла входит легко. Боль уходит, а вместе с ней страх, имя и вопросы.\n\n"
          "Ты улыбаешься проводнице и просишь чаю. Поезд идёт дальше. Тебе хорошо. "
          "Тебе так хорошо, что ты даже не помнишь, кто ты."),
    "e_throne": dict(end="КОНЦОВКА: МАШИНИСТ",
        t="Ты садишься в кресло Корвина. Руки сами ложатся на рычаги. Двигатель благодарно вздыхает.\n\n"
          "Ауэр кланяется: «Добро пожаловать, коллега». За спиной очередной ревизор получает телеграмму "
          "и просыпается в купе №7."),
}


class Game(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("МЕРИДИАН: Поезд без рассвета")
        self.configure(bg=BG)
        self.geometry("1040x700")
        self.minsize(860, 580)
        self.type_job = self.timer_job = None
        self.chars, self.pos, self.typing = [], 0, False
        self.s = State()
        self.build_ui()
        self.reset()
        self.glitch_loop()

    # ---------- интерфейс ----------
    def build_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

        left = tk.Frame(self, bg=PANEL, highlightbackground="#3a3226", highlightthickness=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=12)
        left.rowconfigure(2, weight=1)
        left.columnconfigure(0, weight=1)

        tk.Label(left, text="М Е Р И Д И А Н", bg=PANEL, fg=AMBER, font=("Consolas", 13, "bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 0))
        self.loc = tk.Label(left, text="", bg=PANEL, fg=TEAL, font=MONO)
        self.loc.grid(row=1, column=0, sticky="w", padx=14, pady=(2, 6))

        self.txt = tk.Text(left, wrap="word", bg=PANEL, fg=FG, font=SERIF, bd=0, padx=14, pady=6,
                           spacing3=6, state="disabled", cursor="arrow", highlightthickness=0)
        self.txt.grid(row=2, column=0, sticky="nsew")
        self.txt.tag_configure("clue", foreground=AMBER, underline=True)
        self.txt.tag_configure("end", foreground=AMBER, font=("Consolas", 18, "bold"), spacing3=14)
        self.txt.tag_bind("clue", "<Button-1>", self.on_clue)
        self.txt.tag_bind("clue", "<Enter>", lambda e: self.txt.config(cursor="hand2"))
        self.txt.tag_bind("clue", "<Leave>", lambda e: self.txt.config(cursor="arrow"))
        self.txt.bind("<Button-1>", lambda e: self.skip_typing(), add="+")

        self.tbar = tk.Canvas(left, height=6, bg=PANEL, highlightthickness=0)
        self.tbar.grid(row=3, column=0, sticky="ew", padx=14, pady=4)

        self.chbox = tk.Frame(left, bg=PANEL)
        self.chbox.grid(row=4, column=0, sticky="ew", padx=14, pady=(4, 14))

        right = tk.Frame(self, bg=BG, width=290)
        right.grid(row=0, column=1, sticky="ns", padx=(6, 12), pady=12)
        right.grid_propagate(False)

        def panel(title):
            f = tk.Frame(right, bg=PANEL, highlightbackground="#3a3226", highlightthickness=1)
            f.pack(fill="x", pady=(0, 10))
            tk.Label(f, text=title, bg=PANEL, fg="#9a8a6a", font=("Consolas", 9)).pack(anchor="w", padx=10, pady=(8, 2))
            return f

        p = panel("РАССУДОК")
        self.sbar = tk.Canvas(p, width=260, height=10, bg="#222", highlightthickness=0)
        self.sbar.pack(padx=10, pady=(0, 6))
        self.tv = tk.Label(p, bg=PANEL, fg=FG, font=MONO)
        self.tv.pack(anchor="w", padx=10)
        tk.Label(p, text="ДОВЕРИЕ", bg=PANEL, fg="#9a8a6a", font=("Consolas", 9)).pack(anchor="w", padx=10, pady=(8, 0))
        self.trl = tk.Label(p, bg=PANEL, fg=FG, font=MONO, justify="left")
        self.trl.pack(anchor="w", padx=10, pady=(0, 8))

        p = panel("УЛИКИ")
        self.inv = tk.Label(p, bg=PANEL, fg=AMBER, font=MONO, justify="left", wraplength=260)
        self.inv.pack(anchor="w", padx=10, pady=(0, 8))

        p = panel("ТЕЛЕГРАФ")
        self.log = tk.Text(p, height=12, width=32, wrap="word", bg=PANEL, fg=TEAL, font=("Consolas", 9),
                           bd=0, state="disabled", highlightthickness=0)
        self.log.pack(padx=10, pady=(0, 8))

    def hud(self):
        s = self.s
        self.sbar.delete("all")
        w = int(260 * max(s.san, 0) / 100)
        self.sbar.create_rectangle(0, 0, w, 10, fill=RED if s.san < 30 else TEAL, width=0)
        self.tv.config(text=f"Перегонов до «Зарева»: {s.time}\nРассудок: {max(s.san, 0)}/100")
        lines = []
        for k, n in NAMES.items():
            lvl = max(s.tr[k] + 2, 0)
            lines.append(f"{n:<6} " + "●" * lvl + "○" * (5 - lvl))
        self.trl.config(text="\n".join(lines))
        self.inv.config(text="\n".join("◆ " + CLUES[i][0] for i in s.inv) or "пусто")

    def say(self, m):
        self.log.config(state="normal")
        self.log.insert("1.0", "▸ " + m + "\n\n")
        self.log.config(state="disabled")

    
    def shake(self):
        x, y = self.winfo_x(), self.winfo_y()

        def step(n):
            if n == 0:
                self.geometry(f"+{x}+{y}")
                return
            self.geometry(f"+{x + random.randint(-9, 9)}+{y + random.randint(-7, 7)}")
            self.after(30, lambda: step(n - 1))
        step(9)

    def glitch_loop(self):
        if self.s.san < 30 and random.random() < 0.4:
            self.txt.config(fg=random.choice([RED, TEAL, FG]))
            self.after(90, lambda: self.txt.config(fg=FG))
        self.after(250, self.glitch_loop)

    
    def reset(self):
        self.s = State()
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")
        self.go("start")

    def go(self, sid):
        s = self.s
        for j in (self.type_job, self.timer_job):
            if j:
                self.after_cancel(j)
        self.type_job = self.timer_job = None
        self.tbar.delete("all")
        for w in self.chbox.winfo_children():
            w.destroy()

        sc = SC[sid]
        if "end" not in sc:
            if s.san <= 0:
                sid, sc = "e_mad", SC["e_mad"]
            elif s.time <= 0:
                sid, sc = "e_loop", SC["e_loop"]
        if "enter" in sc:
            sc["enter"](s)
        if "msg" in sc and sid not in s.done:
            self.say(sc["msg"])
        s.done.add(sid)
        self.sc = sc
        self.loc.config(text=sc.get("loc", "—"))
        self.hud()

        
        self.chars = []
        if "end" in sc:
            self.chars += [(c, ("end",)) for c in sc["end"] + "\n"]
        pos = 0
        for m in re.finditer(r"\[\[(\w+)\|([^\]]+)\]\]", sc["t"]):
            self.chars += [(c, ()) for c in sc["t"][pos:m.start()]]
            cid = m.group(1)
            tag = "c_" + cid
            self.txt.tag_configure(tag, foreground=DIM if cid in s.inv else AMBER)
            self.chars += [(c, ("clue", tag)) for c in m.group(2)]
            pos = m.end()
        self.chars += [(c, ()) for c in sc["t"][pos:]]

        self.txt.config(state="normal")
        self.txt.delete("1.0", "end")
        self.txt.config(state="disabled")
        self.pos, self.typing = 0, True
        self.type_next()

    def type_next(self):
        if self.pos >= len(self.chars):
            return self.finish_typing()
        ch, tags = self.chars[self.pos]
        self.pos += 1
        self.txt.config(state="normal")
        self.txt.insert("end", ch, tags)
        self.txt.config(state="disabled")
        self.type_job = self.after(14, self.type_next)

    def skip_typing(self):
        if not self.typing:
            return
        if self.type_job:
            self.after_cancel(self.type_job)
        self.txt.config(state="normal")
        for ch, tags in self.chars[self.pos:]:
            self.txt.insert("end", ch, tags)
        self.txt.config(state="disabled")
        self.pos = len(self.chars)
        self.finish_typing()

    def finish_typing(self):
        if not self.typing:
            return
        self.typing = False
        self.type_job = None
        self.show_buttons()

    def on_clue(self, event):
        idx = self.txt.index(f"@{event.x},{event.y}")
        for t in self.txt.tag_names(idx):
            if t.startswith("c_"):
                cid = t[2:]
                if cid in self.s.inv:
                    return
                self.s.inv.append(cid)
                self.s.san -= 2
                self.txt.tag_configure(t, foreground=DIM)
                self.say("УЛИКА: " + CLUES[cid][1])
                self.hud()
                return

    def show_buttons(self):
        s, sc = self.s, self.sc
        if "end" in sc:
            self.mkbtn("↻ Начать сначала", self.reset, True)
            return
        for c in sc.get("ch", []):
            locked = "req" in c and not c["req"](s)
            gone = "once" in c and ("o_" + c["once"]) in s.done
            if gone:
                label = c["x"] + " (сделано)"
            elif locked:
                label = "🔒 " + c["lock"]
            else:
                label = c["x"]
            self.mkbtn(label, lambda c=c: self.pick(c), not (locked or gone))
        if "timer" in sc:
            self.start_timer(sc["timer"])

    def mkbtn(self, text, cmd, enabled):
        b = tk.Button(self.chbox, text=text, command=cmd, anchor="w", justify="left", wraplength=620,
                      bg="#14110d", fg=FG, activebackground="#2a2216", activeforeground=AMBER,
                      disabledforeground="#5a5040", relief="flat", bd=0, padx=12, pady=8, font=("Georgia", 12),
                      highlightbackground="#5a4a30", highlightthickness=1,
                      state="normal" if enabled else "disabled", cursor="hand2" if enabled else "arrow")
        b.pack(fill="x", pady=3)

    def start_timer(self, t):
        total = t["sec"] * 10
        left = [total]

        def tick():
            left[0] -= 1
            self.tbar.delete("all")
            w = self.tbar.winfo_width() * left[0] / total
            self.tbar.create_rectangle(0, 0, w, 6, fill=RED, width=0)
            if left[0] <= 0:
                self.say("Ты не успел решить. Решили за тебя.")
                self.go(t["to"])
            else:
                self.timer_job = self.after(100, tick)
        tick()

    def pick(self, c):
        s = self.s
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None
        if "once" in c:
            s.done.add("o_" + c["once"])
        s.san = min(100, s.san + c.get("san", 0))
        s.time += c.get("time", 0)
        for k, v in c.get("tr", {}).items():
            s.tr[k] = max(-2, min(3, s.tr[k] + v))
        for i in c.get("add", []):
            if i not in s.inv:
                s.inv.append(i)
                self.say("УЛИКА: " + CLUES[i][1])
        for i in c.get("rm", []):
            if i in s.inv:
                s.inv.remove(i)
        if c.get("shake") or c.get("san", 0) <= -8:
            self.shake()
        to = c["to"](s) if callable(c["to"]) else c["to"]
        self.go(to)


if __name__ == "__main__":
    Game().mainloop()