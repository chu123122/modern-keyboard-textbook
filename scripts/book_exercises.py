"""Original examples. Quarter-note units; C4 = MIDI 60. No third-party music."""
from copy import deepcopy


def n(pitches, duration=1, finger=None, tie=None):
    out = {"pitches": pitches.split() if pitches != "r" else [], "duration": duration}
    if finger is not None:
        out["finger"] = finger
    if tie:
        out["tie"] = tie
    return out


def line(text, duration=1, fingers=None):
    return [n(p, duration, fingers[i] if fingers else None) for i, p in enumerate(text.split())]


def rest(bars, length=4):
    return [[n("r", length)] for _ in range(bars)]


EXERCISES = []


def add(id, title, rh, lh=None, *, chords=None, key=0, meter=(4, 4), bpm=60,
        note="", pedal=False, left_role="left-hand"):
    EXERCISES.append(dict(id=id, title=title, rh=rh, lh=lh or rest(len(rh), meter[0]*4/meter[1]),
                          chords=chords or [], key=key, meter=list(meter), bpm=bpm,
                          note=note, pedal=pedal, left_role=left_role))


add("E01", "五个相邻音", [line("C4 D4 E4 F4", fingers=[1,2,3,4]),
    line("G4 F4 E4 D4", fingers=[5,4,3,2]), [n("C4",4,1)]],
    note="右手。中央 C 为 C4。先认黑键分组，再找到 C4。")
add("E02", "让休止也占时间", [[n("C4"),n("C4"),n("C4",2)],
    [n("r"),n("C4"),n("C4"),n("C4")], [n("C4",2),n("C4",2)], [n("C4",4)]],
    note="右手单音；第二小节第一拍不弹，但继续数拍。")
add("E03", "顺着方向读", [line("C4 D4 E4 G4"),line("F4 E4 D4 C4")],
    note="先从已知的 C4 找方向；第一个跳进是 E4 到 G4。")
add("E04", "左手自己的旋律", rest(2), [line("C3 D3 E3 G3",fingers=[5,4,3,1]),
    line("F3 E3 D3 C3",fingers=[2,3,4,5])], note="只弹左手；低音谱表不等于只能弹伴奏。")
add("E05", "长低音托住旋律", [line("C4 D4 E4 G4",fingers=[1,2,3,5]),
    line("F4 E4 D4 C4",fingers=[4,3,2,1]),line("E4 G4 F4 D4",fingers=[3,5,4,2]),[n("C4",4,1)]],
    [[n("C3",4,5)],[n("F3",4,2)],[n("G3",4,1)],[n("C3",4,5)]],
    note="左手每小节只开始一次，并保持四拍；右手音变时，左手不跟着重弹。")
add("E06", "两手交替进入", [[n("r"),n("E4"),n("r"),n("G4")],
    [n("r"),n("F4"),n("r"),n("A4")], [n("r"),n("D4"),n("r"),n("F4")], [n("C4",4)]],
    [[n("C3"),n("r"),n("G3"),n("r")],[n("F3"),n("r"),n("C3"),n("r")],
     [n("G3"),n("r"),n("D3"),n("r")],[n("C3",4)]],
    note="前三小节按左、右、左、右交替；最后一小节双手同时进入。第二小节右手需移动手位。")

FIRST = [line("C4 E4 G4 E4"),[n("F4",2),n("E4"),n("D4")],
    line("E4 G4 F4 D4"),[n("C4",2),n("D4"),n("E4")],line("F4 G4 E4 F4"),
    line("E4 G4 E4 D4"),line("D4 F4 E4 D4"),[n("C4",4)]]
add("E07", "小曲：一步一步", FIRST, [[n(p,4)] for p in ["C3","F3","C3","C3","F3","C3","G3","C3"]],
    bpm=64, note="八小节原创小曲。右手范围 C4–G4；建议五指对应这五个音。全曲先不用踏板。")
add("E08", "C 大调的一次换指", [line("C4 D4 E4 F4",fingers=[1,2,3,1]),
    line("G4 A4 B4 C5",fingers=[2,3,4,5]),line("C5 B4 A4 G4",fingers=[5,4,3,2]),
    line("F4 E4 D4 C4",fingers=[1,3,2,1])], note="同音重复处重新触键。音阶指法是建议，移动应平顺。")
add("E09", "G 大调与 F♯", [line("G4 A4 B4 C5",fingers=[1,2,3,1]),
    line("D5 E5 F#5 G5",fingers=[2,3,4,5]),line("G5 F#5 E5 D5",fingers=[5,4,3,2]),
    line("C5 B4 A4 G4",fingers=[1,3,2,1])],key=1,note="调号使本谱所有 F 默认升高；本例从 G4 开始。")
add("E10", "F 大调与 B♭", [line("F4 G4 A4 Bb4",fingers=[1,2,3,4]),
    line("C5 D5 E5 F5",fingers=[1,2,3,4]),line("F5 E5 D5 C5",fingers=[4,3,2,1]),
    line("Bb4 A4 G4 F4",fingers=[4,3,2,1])],key=-1,note="F 大调右手上行先用 4 指弹 B♭，再把拇指移动到 C。")
add("E11", "同根音的四种三和弦", [[n(p,4)] for p in ["C4 E4 G4","C4 Eb4 G4","C4 Eb4 Gb4","C4 E4 G#4"]],
    chords=["C","Cm","Cdim","Caug"],note="听比较时每种单独停留；这不是要求背诵的和声进行。")
add("E12", "保留共同音的连接", [[n(p,4)] for p in ["C4 E4 G4","C4 F4 A4","B3 D4 G4","C4 E4 G4"]],
    [[n(p,4)] for p in ["C3","F3","G3","C3"]], chords=["C","F","G","C"],
    note="右手改变排列，左手始终弹相应根音。整体四个和弦都处于原位。")
add("E13", "低音决定整体转位", [[n("C4 E4 G4",4)] for _ in range(4)],
    [[n(p,4)] for p in ["C3","E3","G3","C3"]],chords=["C","C/E","C/G","C"],
    note="根音始终是 C；低音依次为 C、E、G、C。")
MELODY4=[line("C4 E4 G4 E4"),[n("F4",2),n("E4"),n("D4")],line("D4 F4 E4 D4"),[n("C4",4)]]
add("E14", "旋律与两音和声", MELODY4,
    [[n(p,4)] for p in ["C3 E3","F3 A3","G3 B3","C3 E3"]],chords=["C","F","G","C"],
    note="左手采用根音与三音，省略五音；右手旋律应清楚地浮在上面。")
BROKEN=["C3 G3 E3 G3","F2 C3 A2 C3","G2 D3 B2 D3","C3 G3 E3 G3"]
add("E15", "四分音符分解伴奏", MELODY4,[line(p) for p in BROKEN],chords=["C","F","G","C"],
    note="左手每小节音型为根—五—三—五；F2 在 C3 下方，先确认八度。")
add("E16", "八分音符分解伴奏", MELODY4,[line(p+" "+p,.5) for p in BROKEN],
    chords=["C","F","G","C"],bpm=56,note="每拍两格。增加密度后仍保持旋律突出，不急于提高速度。")
add("E17", "换和声时换踏板", MELODY4,[[n(p,4)] for p in ["C3 E3 G3","F2 A2 C3","G2 B2 D3","C3 E3 G3"]],
    chords=["C","F","G","C"],pedal=True,note="有踏板示范：每小节开始后稍晚踩下，下一小节开始前抬起。本例是入门分段练习，非通用踏板公式。")
add("E18", "切分与连音线", [[n("r",.5),n("E4",.5,tie="start"),n("E4",1,tie="stop"),n("G4"),n("E4")],
    [n("D4",.5),n("E4",.5),n("F4"),n("E4"),n("D4")],
    [n("r",.5),n("D4",.5,tie="start"),n("D4",1,tie="stop"),n("F4"),n("D4")],[n("C4",4)]],
    [line("C3 G3 C3 G3"),line("F2 C3 F2 C3"),line("G2 D3 G2 D3"),[n("C3",4)]],
    chords=["C","F","G","C"],bpm=56,note="连音线连接同音，右手 E4 在第一小节第二拍不重新弹；第三小节 D4 同理。")
add("E19", "6/8 的两个大拍", [line("E4 G4 C5 B4 G4 E4",.5),line("F4 A4 C5 A4 F4 A4",.5),
    line("D4 G4 B4 G4 F4 D4",.5),[n("C4",3)]],
    [[n("C3",1.5),n("G3",1.5)],[n("F2",1.5),n("C3",1.5)],
     [n("G2",1.5),n("D3",1.5)],[n("C3",3)]],meter=(6,8),bpm=90,
    chords=["C","F","G","C"],note="附点四分音符 = 60。每大拍三格；预备数两个大拍。")
add("E20", "小调小曲：晚灯", [line("A4 C5 E5 C5"),[n("D5",2),n("C5"),n("B4")],
    line("C5 E5 D5 B4"),[n("A4",2),n("B4"),n("C5")],line("D5 F5 E5 D5"),
    line("C5 E5 C5 B4"),line("B4 D5 C5 B4"),[n("A4",4)]],
    [line(p) for p in ["A2 E3 C3 E3","D3 A3 F3 A3","E3 B3 G#3 B3","A2 E3 C3 E3",
     "D3 A3 F3 A3","A2 E3 C3 E3","E3 B3 G#3 B3","A2 E3 C3 E3"]],
    chords=["Am","Dm","E7","Am","Dm","Am","E7","Am"],bpm=64,
    note="第 3 小节 E7 的七音由右手 D5 提供；第 7 小节同样如此。G♯ 用于通向 A 的属和声。")
add("E21", "听清七和弦性质", [[n(p,4)] for p in ["E4 G4 B4","E4 G4 Bb4","B3 D4 F4","C4 E4 G4"]],
    [[n(p,4)] for p in ["C3","C3","G2","A2"]],chords=["Cmaj7","C7","G7","Am7"],
    note="四个和弦的性质比较，结合两手判断全部和弦音；不是通用的功能进行。")
FINAL=[line("E4 G4 A4 G4"),[n("F4"),n("A4"),n("G4",2)],line("E4 G4 D5 B4"),[n("C5",2),n("G4",2)],
    line("A4 C5 B4 A4"),line("G4 E4 F4 G4"),[n("F4"),n("E4"),n("D4",2)],[n("C4",4)],
    [n("C5"),n("B4"),n("A4",2)],[n("A4"),n("G4"),n("F4",2)],line("G4 F4 E4 D4"),[n("E4",2),n("G4",2)],
    [n("E4",.5),n("G4",.5),n("A4"),n("G4"),n("E4")],line("F4 A4 G4 F4"),line("D4 F4 E4 D4"),[n("C4",4)]]
progress=["C","F","G","C","Am","C","G","C","Am","F","G7","C","C","F","G","C"]
patterns={"C":"C3 G3 E3 G3","F":"F2 C3 A2 C3","G":"G2 D3 B2 D3","Am":"A2 E3 C3 E3"}
final_left=[line(patterns[c]) for c in progress[:8]]
final_left += [[n(p,2),n(p,2)] for p in ["A2 C3","F3 A3","G3 B3 F4","C3 E3"]]
# Keep all keyboard accompaniment below the lowest simultaneous melody pitch.
final_left[10]=[n("G2 B2 F3",2),n("G2 B2 F3",2)]
final_left += [line(patterns[c]) for c in progress[12:15]]+[[n("C3 E3 G3",4)]]
add("E22", "阶段作品：窗边小曲", FINAL, final_left,chords=progress,bpm=68,
    note="十六小节原创作品，结构 A（1–8）—B（9–12）—A′（13–16）。第 9–12 小节有意降低伴奏密度。")
add("E23", "有贝斯时的键盘留白", [[n("E4 G4"),n("r"),n("E4 G4"),n("r")],
    [n("F4 A4"),n("r"),n("F4 A4"),n("r")],[n("B3 F4"),n("r"),n("B3 F4"),n("r")],[n("E4 G4",4)]],
    [[n(p,4)] for p in ["C3","F2","G2","C3"]],chords=["C","F","G7","C"],
    left_role="bass-reference",note="下谱表是贝斯参照，不是要求键盘左手弹。先听双手了解配合，再只弹上谱表。")
add("E24", "把短句移到 G 大调", [line("G4 A4 B4 D5"),line("C5 B4 A4 G4"),
    line("B4 D5 C5 A4"),[n("G4",4)]],[[n(p,4)] for p in ["G3","C4","D4","G3"]],key=1,
    note="E05 整体上移纯五度。听相同的音级关系；不是只按相同白键位置。")

EXERCISE_BY_ID={e["id"]:e for e in EXERCISES}
