# Content Review Crew

## Proje Hakkında

Kullanıcının verdiği kısa bir metni, blog taslağını veya teknik açıklamayı birden fazla CrewAI agent'ı ile farklı açılardan inceleyen küçük bir öğrenme projesi.

Amaç bir ürün geliştirmek değil, CrewAI'nin temel parçalarını (Agent, Task, Crew, custom tool, structured output, hierarchical process, manager, kickoff) çalışan bir örnek üzerinde öğrenmek.

## Mimari

```
Kullanıcı (terminal veya Gradio)
 ↓
Review Manager
 ├── Clarity Reviewer    → count_words, count_long_sentences
 ├── Claim Reviewer      → find_absolute_phrases, ClaimReview (Pydantic)
 └── Improvement Editor
 ↓
Final değerlendirme (düz metin)
```

Proje `crewai create crew --classic` ile oluşturuldu. Agent ve task tanımları YAML dosyalarında, Python bağlantıları `crew.py` içinde.

```
src/content_review_crew/
├── config/agents.yaml   agent ve manager tanımları
├── config/tasks.yaml    task açıklamaları ve beklenen çıktılar
├── crew.py              Agent, Task ve Crew nesneleri
├── llm.py               Groq bağlantısı
├── models.py            ClaimReview modeli
├── tools/text_tools.py  custom tool'lar
├── main.py              terminal girişi ve kickoff
├── app.py               Gradio arayüzü
└── check_llm.py         LLM bağlantı testi
```

## Agentlar

| Agent | Görev | Tool |
|---|---|---|
| Review Manager | Task'leri uygun agent'a delege eder, kendisi inceleme yapmaz | CrewAI'nin delegasyon tool'ları |
| Clarity Reviewer | Okunabilirlik, uzun cümleler, tekrar ve belirsiz ifadeler | `count_words`, `count_long_sentences` |
| Claim Reviewer | İddiaları bulur; yorum, tahmin ve doğrulanabilir ifadeleri ayırır | `find_absolute_phrases` |
| Improvement Editor | Önceki incelemeleri birleştirir, öneriler ve revize metin yazar | yok |

Manager `agents.yaml` içinde tanımlı ama `@agent` ile işaretlenmedi. CrewAI, `manager_agent` olarak verilen agent'ın `agents` listesinde bulunmasına izin vermiyor.

## Görevler

| Task | Çıktı |
|---|---|
| `clarity_review_task` | Madde işaretli okunabilirlik değerlendirmesi |
| `claim_review_task` | `ClaimReview` nesnesi |
| `improvement_task` | Sabit bölümlü final değerlendirme |

`improvement_task`, `context` ile ilk iki task'in çıktısını alır. Final metin şu bölümlerden oluşur: İnceleme Özeti, Anlatım, Destek Gerektiren İddialar, Riskli İfadeler, Öneriler, Revize Metin.

## Custom Tools

Tool'lar `crewai.tools.tool` dekoratörüyle yazıldı. Hepsi saf Python ile çalışır ve harici API kullanmaz.

- `count_words`: kelime ve cümle sayısını, ortalama cümle uzunluğunu döndürür.
- `count_long_sentences`: 20 kelimeden uzun cümleleri listeler.
- `find_absolute_phrases`: "bütün", "her", "hiç", "kesinlikle", "artık" gibi kesinlik bildiren kelimeleri tam kelime eşleşmesiyle bulur.

Agent bir tool'u yalnızca tool o agent'a verildiyse kullanabilir. Task açıklamasında tool'un adı geçince model onu daha tutarlı çağırıyor. `verbose=True` ile her çağrı terminalde görünür:

```
Tool Execution Started (#1)
Tool: find_absolute_phrases
Args: {'text': 'Bu framework her projede kesinlikle ...'}

Tool Execution Completed (#1)
Output: Absolute phrases: her, hiç, kesinlikle
```

## Structured Output

Yalnızca Claim Reviewer'ın task'i yapılandırılmış çıktı üretir:

```python
class ClaimReview(BaseModel):
    claims: list[str]
    unsupported_claims: list[str]
    absolute_phrases: list[str]
```

`Task(output_pydantic=ClaimReview)` verildiğinde CrewAI, LLM'in cevabını bu modele dönüştürür. Sonuca `result.tasks_output[1].pydantic` ile erişilir. Final cevap bilerek düz metin bırakıldı, çünkü kullanıcıya okunabilir bir değerlendirme gösteriliyor.

## Hierarchical Process

Crew, `Process.hierarchical` ve özel bir `manager_agent` ile çalışır. Hierarchical modda her task'i manager yürütür. İşi coworker'lara `delegate_work_to_coworker` ve `ask_question_to_coworker` tool'larıyla aktarır.

Deneme sırasında görülenler:

- Task'te `agent` tanımlı değilse manager tüm agent'lar arasından seçim yapar. `agent` tanımlıysa delegasyon yalnızca o agent ile sınırlanır.
- `gpt-oss-20b` manager, final task'i talimatlar netleştirilse de Improvement Editor'a vermedi. Reviewer'lara işi tekrar yaptırıp metni kendisi yazdı. Bu yüzden yalnızca `improvement_task` için `agent: improvement_editor` tanımlı. İlk iki task'te seçim manager'da.
- Coworker'lar yalnızca manager'ın gönderdiği bilgiyi görür. Manager'ın backstory'sinde orijinal metni ve önceki sonuçları her delegasyonda göndermesi isteniyor.

## Kullanılan Model

Groq üzerinde `openai/gpt-oss-20b`. Bağlantı, CrewAI'nin kendi OpenAI-compatible istemcisiyle kuruluyor; LiteLLM kullanılmıyor.

```python
LLM(
    model="openai/gpt-oss-20b",
    provider="openai",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"],
)
```

`provider="openai"` gerekli. Verilmezse CrewAI `openai/` önekini provider adı olarak yorumlayıp siliyor ve Groq'a `gpt-oss-20b` gidiyor. Gönderilen model adı `OPENAI_LOG=debug uv run check_llm` ile istek gövdesinde görülebilir.

Geliştirme sırasında kullanılan Groq hesabında bu model için günlük 200.000 token limiti vardı. Bir hierarchical çalıştırma yaklaşık 20-30 bin token harcıyor. Limit dolunca istekler `429` hatası döner ve kota zamanla yeniden açılır.

## Kurulum

Gereksinimler: Python 3.10-3.13, [uv](https://docs.astral.sh/uv/), Groq API anahtarı.

```bash
uv tool install crewai
git clone <repo-url>
cd content-review-crew
crewai install
```

`.env.example` dosyasını `.env` olarak kopyalayıp anahtarı ekleyin:

```
GROQ_API_KEY=gsk_...
```

## Çalıştırma

LLM bağlantı testi:

```bash
uv run check_llm
```

Terminal:

```bash
crewai run
```

Metni yazıp boş bir satırda Enter'a basın. Hiçbir şey yazılmazsa örnek metin kullanılır.

Gradio arayüzü:

```bash
uv run review_ui
```

Ardından `http://127.0.0.1:7860` adresini açın, metni girip Review butonuna basın.

## Örnek Kullanım

Girdi:

```
Bu framework her projede kesinlikle en iyi performansı verir.
Başka bir araç kullanmaya hiç gerek yok.
```

Structured claim review:

```json
{
  "claims": [
    "Bu framework her projede kesinlikle en iyi performansı verir.",
    "Başka bir araç kullanmaya hiç gerek yok."
  ],
  "unsupported_claims": [
    "Bu framework her projede kesinlikle en iyi performansı verir.",
    "Başka bir araç kullanmaya hiç gerek yok."
  ],
  "absolute_phrases": [
    "kesinlikle"
  ]
}
```

Final değerlendirme:

```
İnceleme Özeti
Metin iki güçlü iddia içeriyor: "Bu framework her projede kesinlikle en iyi
performansı verir" ve "Başka bir araç kullanmaya hiç gerek yok." Bu ifadeler
somut veri veya bağlamdan yoksun ve "kesinlikle" gibi mutlak bir kelimeyle
güçlendirildiği için desteklenmemiş iddialar olarak değerlendiriliyor.

Anlatım
Metin kısa, anlaşılır ve özlü; ancak mutlak ifadeler ve desteklenmemiş
iddialar okuyucuyu yanıltma riski taşıyor.

Destek Gerektiren İddialar
- "Bu framework her projede kesinlikle en iyi performansı verir"
- "Başka bir araç kullanmaya hiç gerek yok"

Riskli İfadeler
- "kesinlikle"
- "hiç gerek yok"

Öneriler
- Performans ölçütleri ve karşılaştırmalı test sonuçları ekleyin.
- Hangi proje türlerinde üstünlük sağlandığını belirtin.
- "kesinlikle" yerine "çoğu durumda" veya "genellikle" gibi ifadeler kullanın.
- Alternatif araçların hangi senaryolarda tercih edilebileceğini tanımlayın.
- İddiaları destekleyen rapor, makale veya kullanıcı deneyimlerini referans gösterin.

Revize Metin
Bu framework, çoğu projede yüksek performans sağlar; başka bir araç
kullanmaya gerek kalmaz.
```

Bu çıktı, `find_absolute_phrases` tam kelime eşleşmesine geçmeden önceki sürümle alındı. O sürüm "her" ve "hiç" kelimelerini bulamıyordu. Model çıktısı her çalıştırmada değişebilir; örnekteki revize metin de iddiayı hâlâ fazla kesin bırakıyor.

## Öğrendiklerim

- `crewai create crew` artık varsayılan olarak JSON proje oluşturuyor. Python/YAML yapısı için `--classic` gerekiyor.
- YAML'da `role: >` kullanılınca role sonuna satır sonu ekleniyor. Manager coworker'ları role adıyla bulduğu için role'ler düz string yazıldı.
- `LLM` sınıfı model adındaki önekten provider seçiyor. OpenAI-compatible bir servise önekli model adı göndermek için `provider` açıkça verilmeli.
- Hierarchical process'te manager modelinin kalitesi akışı doğrudan etkiliyor. Küçük bir modelle delegasyon kararları tutarsız olabiliyor ve task'e `agent` atamak bu kararı sınırlamanın yolu.
- `output_pydantic` yalnızca bir task'te kullanılınca hem yapılandırılmış veri hem okunabilir final metin elde edilebiliyor.
- Hierarchical bir crew, sequential olana göre çok daha fazla LLM çağrısı yapıyor. Ücretsiz API limitleri birkaç test çalıştırmasında doluyor.
- `kickoff()` dönüş tipi `CrewOutput | CrewStreamingOutput`. Streaming kapalıyken `isinstance` kontrolü tip denetleyicisi için yeterli.
