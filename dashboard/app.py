"""
Dashboard Huttopia — Voice of Customer
Deux vues : Commerciale (KPIs, alertes) et Marketing (thèmes, verbatims)

Usage :
    cd huttopia-voc
    streamlit run dashboard/app.py
"""

import sys
import ast
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Chemins ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH    = PROJECT_ROOT / "data" / "processed" / "huttopia_reviews_master.csv"
sys.path.insert(0, str(PROJECT_ROOT / "config"))
from labels import THEME_DISPLAY_NAMES

# ── Palette & constantes ─────────────────────────────────────────────────────
COLOR_PRIMARY   = "#2D6A4F"   # Vert forêt
COLOR_SECONDARY = "#74C69D"   # Vert clair
COLOR_ACCENT    = "#D62828"   # Rouge alerte
COLOR_WARN      = "#F4A261"   # Orange attention
COLOR_OK        = "#52B788"   # Vert OK
COLOR_BG        = "#F8F9FA"

PALETTE_CAMPINGS = px.colors.qualitative.Safe
PALETTE_THEMES   = [
    "#2D6A4F", "#52B788", "#74C69D", "#95D5B2",
    "#B7E4C7", "#D8F3DC", "#F4A261",
]

NOTE_GLOBALE_HUTTOPIA = 3.65  # Référence

# ── Config page ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Huttopia — Voice of Customer",
    page_icon="🏕️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personnalisé ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Source+Sans+3:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Source Sans 3', sans-serif;
    }
    h1, h2, h3 { font-family: 'Playfair Display', serif; color: #1B4332; }

    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 4px solid #2D6A4F;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .metric-card.warn  { border-left-color: #F4A261; }
    .metric-card.alert { border-left-color: #D62828; }

    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-green  { background: #D8F3DC; color: #1B4332; }
    .badge-orange { background: #FFE8CC; color: #7C4A00; }
    .badge-red    { background: #FFDDD5; color: #7C0000; }

    .verbatim {
        background: #F8F9FA;
        border-left: 3px solid #74C69D;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 10px;
        font-size: 14px;
        line-height: 1.6;
    }
    .source-tag {
        font-size: 11px;
        color: #6C757D;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] { font-size: 2rem !important; }
</style>
""", unsafe_allow_html=True)


# ── Chargement & cache ────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")

    # Normalise les noms d'établissements (sécurité si ancien fichier)
    etablissement_map = {
        "sud_ardeche": "Sud_Ardeche", "gorges_du_verdon": "Gorges_du_Verdon",
        "font_romeu": "Font_Romeu", "le_moulin": "Le_Moulin",
        "marque globale": "Marque_Globale",
    }
    df["nom_etablissement"] = df["nom_etablissement"].apply(
        lambda x: etablissement_map.get(str(x).lower(), x)
    )

    # Exclut Marque_Globale et Inconnu des analyses par camping
    df["camping"] = df["nom_etablissement"].apply(
        lambda x: x if x not in ("Marque_Globale", "Inconnu") else None
    )

    # Sentiment si disponible
    if "sentiment_label" not in df.columns:
        df["sentiment_label"] = None
    if "sentiment_score" not in df.columns:
        df["sentiment_score"] = None

    # Theme display
    if "theme_label" in df.columns:
        df["theme_display"] = df["theme_label"].map(THEME_DISPLAY_NAMES).fillna(df["theme_label"])
    else:
        df["theme_display"] = "Non classifié"
        df["theme_label"]   = "non classifié"

    # Date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    return df


def note_to_badge(note: float) -> str:
    if note >= 3.8:
        return f'<span class="badge badge-green">✓ {note:.2f}/5</span>'
    elif note >= 3.4:
        return f'<span class="badge badge-orange">⚠ {note:.2f}/5</span>'
    else:
        return f'<span class="badge badge-red">✗ {note:.2f}/5</span>'


# ── Sidebar filtres ───────────────────────────────────────────────────────────
def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.markdown("## 🎛️ Filtres")

    campings = sorted([c for c in df["nom_etablissement"].unique()
                       if c not in ("Marque_Globale", "Inconnu")])
    selected_campings = st.sidebar.multiselect(
        "Campings", campings, default=campings
    )

    sources = sorted(df["source"].unique())
    selected_sources = st.sidebar.multiselect(
        "Sources", sources, default=sources
    )

    langues = sorted(df["langue"].dropna().unique())
    selected_langues = st.sidebar.multiselect(
        "Langues", langues, default=langues
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"*Corpus : {len(df)} avis | "
        f"{df['nom_etablissement'].nunique()} campings*"
    )

    # Marque_Globale (Trustpilot) inclus si la source Trustpilot est sélectionnée
    mask = (
        (
            df["nom_etablissement"].isin(selected_campings) |
            df["nom_etablissement"].isin(["Marque_Globale", "Inconnu"])
        ) &
        df["source"].isin(selected_sources) &
        df["langue"].isin(selected_langues)
    )
    return df[mask].copy()


# ── VUE COMMERCIALE ───────────────────────────────────────────────────────────
def vue_commerciale(df: pd.DataFrame) -> None:
    st.markdown("## 📊 Vue Commerciale")
    st.caption("Synthèse des performances clients par camping — indicateurs décisionnels")

    # ── KPIs globaux ──────────────────────────────────────────────────────────
    col1, col2, col3, col4, col5 = st.columns(5)

    note_moy    = df["note_std"].mean()
    nb_avis     = len(df)
    nb_camping  = df[df["camping"].notna()]["camping"].nunique()

    has_sentiment = df["sentiment_label"].notna().any()
    pct_positif   = (df["sentiment_label"] == "Positif").sum() / len(df) * 100 if has_sentiment else None
    pct_negatif   = (df["sentiment_label"] == "Négatif").sum() / len(df) * 100 if has_sentiment else None
    nps_proxy     = round(pct_positif - pct_negatif, 1) if has_sentiment else None

    with col1:
        delta = f"{note_moy - NOTE_GLOBALE_HUTTOPIA:+.2f} vs corpus"
        st.metric("Note moyenne", f"{note_moy:.2f} / 5", delta)
    with col2:
        st.metric("Avis analysés", f"{nb_avis:,}".replace(",", " "))
    with col3:
        st.metric("Campings couverts", nb_camping)
    with col4:
        if pct_positif is not None:
            st.metric("Avis positifs", f"{pct_positif:.0f}%")
        else:
            st.metric("Sources", df["source"].nunique())
    with col5:
        if nps_proxy is not None:
            st.metric(
                "NPS proxy",
                f"{nps_proxy:.0f}",
                help="(% Positif - % Négatif) — approximation du Net Promoter Score. "
                     "Non comparable à un NPS officiel mesuré en enquête.",
            )
        else:
            st.metric("Sources", df["source"].nunique())

    st.markdown("---")

    # ── Notes par camping ─────────────────────────────────────────────────────
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### Notes moyennes par camping")
        stats = (
            df[df["camping"].notna()]
            .groupby("camping")["note_std"]
            .agg(["mean", "count"])
            .reset_index()
            .rename(columns={"mean": "note_moy", "count": "nb_avis", "camping": "Camping"})
            .sort_values("note_moy")
        )

        fig = px.bar(
            stats,
            x="note_moy",
            y="Camping",
            orientation="h",
            color="note_moy",
            color_continuous_scale=["#D62828", "#F4A261", "#52B788"],
            range_color=[2.5, 5.0],
            text=stats["note_moy"].round(2),
            hover_data={"nb_avis": True, "note_moy": ":.2f"},
            labels={"note_moy": "Note /5", "Camping": ""},
        )
        fig.add_vline(
            x=df["note_std"].mean(),
            line_dash="dash",
            line_color="#2D6A4F",
            annotation_text=f"Moy. {df['note_std'].mean():.2f}",
            annotation_position="top right",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=380, showlegend=False,
            coloraxis_showscale=False,
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=10, r=40, t=10, b=10),
            xaxis=dict(range=[0, 5.5], gridcolor="#F0F0F0"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("### Répartition des sources")
        source_stats = df.groupby("source").agg(
            nb_avis=("note_std", "count"),
            note_moy=("note_std", "mean")
        ).reset_index()

        fig2 = px.pie(
            source_stats,
            values="nb_avis",
            names="source",
            color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY, COLOR_WARN],
            hole=0.5,
        )
        fig2.update_traces(
            textinfo="percent+label",
            textposition="outside",
            rotation=40,
            hovertemplate="<b>%{label}</b><br>%{value} avis<br>Note moy: " +
                          source_stats["note_moy"].round(2).astype(str).values[0],
        )
        fig2.update_layout(
            height=280, showlegend=False,
            margin=dict(l=40, r=40, t=40, b=40),
            paper_bgcolor="white",
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("**⚠️ Note sur les biais de plateforme**")
        st.caption(
            "Booking (note moy. ~4.3) reflète des clients satisfaits "
            "post-séjour. Trustpilot (~1.2) attire principalement les "
            "insatisfaits. Google Maps (~3.0) est le plus représentatif."
        )

    st.markdown("---")

    # ── Tableau synthétique ───────────────────────────────────────────────────
    st.markdown("### Tableau de bord par camping")

    tableau = (
        df[df["camping"].notna()]
        .groupby("camping")
        .agg(
            nb_avis=("note_std", "count"),
            note_moy=("note_std", "mean"),
            theme_dominant=("theme_label", lambda x: x.mode()[0] if len(x) > 0 else "—"),
            pct_positif=("sentiment_label", lambda x: (x == "Positif").sum() / len(x) * 100),
        )
        .reset_index()
        .rename(columns={"camping": "Camping"})
        .sort_values("note_moy", ascending=False)
    )
    tableau["Note"] = tableau["note_moy"].apply(lambda x: note_to_badge(round(x, 2)))
    tableau["Thème dominant"] = tableau["theme_dominant"].map(THEME_DISPLAY_NAMES).fillna("—")
    tableau["Avis"] = tableau["nb_avis"]
    tableau["% Positif"] = tableau["pct_positif"].apply(lambda x: f"{x:.0f}%")

    moy = tableau["note_moy"].mean()
    tableau["Statut"] = tableau["note_moy"].apply(
        lambda x: "🟢 OK" if x >= 3.8 else ("🟡 Attention" if x >= 3.4 else "🔴 Alerte")
    )

    st.write(
        tableau[["Camping", "Note", "% Positif", "Avis", "Thème dominant", "Statut"]]
        .to_html(escape=False, index=False),
        unsafe_allow_html=True,
    )


# ── VUE MARKETING ─────────────────────────────────────────────────────────────
def vue_marketing(df: pd.DataFrame) -> None:
    st.markdown("## 🎯 Vue Marketing")
    st.caption("Distribution thématique, analyse par camping et verbatims clients")

    # ── Distribution des thèmes ───────────────────────────────────────────────
    col1, col2 = st.columns([2, 3])

    with col1:
        st.markdown("### Thèmes abordés")
        theme_counts = (
            df.groupby("theme_display")["note_std"]
            .agg(["count", "mean"])
            .reset_index()
            .rename(columns={"count": "nb", "mean": "note_moy", "theme_display": "Thème"})
            .sort_values("nb", ascending=False)
        )

        fig = px.pie(
            theme_counts,
            values="nb",
            names="Thème",
            color_discrete_sequence=PALETTE_THEMES,
            hole=0.45,
        )
        fig.update_traces(textinfo="percent+label", textfont_size=11)
        fig.update_layout(
            height=320, showlegend=False,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Note moyenne par thème")
        fig2 = px.bar(
            theme_counts.sort_values("note_moy"),
            x="note_moy",
            y="Thème",
            orientation="h",
            color="note_moy",
            color_continuous_scale=["#D62828", "#F4A261", "#52B788"],
            range_color=[2.5, 5.0],
            text=theme_counts.sort_values("note_moy")["note_moy"].round(2),
            labels={"note_moy": "Note /5", "Thème": ""},
        )
        fig2.add_vline(
            x=df["note_std"].mean(),
            line_dash="dash",
            line_color="#2D6A4F",
            annotation_text=f"Moy. {df['note_std'].mean():.2f}",
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(
            height=320, showlegend=False,
            coloraxis_showscale=False,
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=10, r=40, t=10, b=10),
            xaxis=dict(range=[0, 5.5], gridcolor="#F0F0F0"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Heatmap thème × camping ───────────────────────────────────────────────
    st.markdown("### Thèmes par camping — note moyenne")
    st.caption("Chaque cellule = note moyenne des avis classés dans ce thème pour ce camping")

    pivot = (
        df[df["camping"].notna()]
        .groupby(["camping", "theme_display"])["note_std"]
        .mean()
        .unstack(fill_value=None)
        .round(2)
    )

    fig3 = px.imshow(
        pivot,
        color_continuous_scale=["#D62828", "#F4A261", "#95D5B2", "#2D6A4F"],
        range_color=[2.0, 5.0],
        aspect="auto",
        text_auto=True,
        labels={"color": "Note /5", "x": "Thème", "y": "Camping"},
    )
    fig3.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white",
        coloraxis_colorbar=dict(title="Note /5"),
        xaxis=dict(side="bottom"),
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ── Sentiment par thème ───────────────────────────────────────────────────
    st.markdown("### Sentiment par thème")
    st.caption("% d'avis positifs / neutres / négatifs par thème")

    if df["sentiment_label"].notna().any():
        sent_theme = (
            df.groupby(["theme_display", "sentiment_label"])
            .size()
            .unstack(fill_value=0)
            .reset_index()
        )
        # Assure que les 3 colonnes existent
        for col in ["Positif", "Neutre", "Négatif"]:
            if col not in sent_theme.columns:
                sent_theme[col] = 0

        sent_theme["total"] = sent_theme[["Positif", "Neutre", "Négatif"]].sum(axis=1)
        sent_theme["% Positif"] = (sent_theme["Positif"] / sent_theme["total"] * 100).round(1)
        sent_theme["% Neutre"]  = (sent_theme["Neutre"]  / sent_theme["total"] * 100).round(1)
        sent_theme["% Négatif"] = (sent_theme["Négatif"] / sent_theme["total"] * 100).round(1)
        sent_theme = sent_theme.sort_values("% Positif", ascending=True)

        fig_sent = go.Figure()
        fig_sent.add_trace(go.Bar(
            y=sent_theme["theme_display"], x=sent_theme["% Positif"],
            name="Positif", orientation="h",
            marker_color=COLOR_OK,
            text=sent_theme["% Positif"].apply(lambda x: f"{x:.0f}%"),
            textposition="inside",
        ))
        fig_sent.add_trace(go.Bar(
            y=sent_theme["theme_display"], x=sent_theme["% Neutre"],
            name="Neutre", orientation="h",
            marker_color="#ADB5BD",
            text=sent_theme["% Neutre"].apply(lambda x: f"{x:.0f}%" if x > 5 else ""),
            textposition="inside",
        ))
        fig_sent.add_trace(go.Bar(
            y=sent_theme["theme_display"], x=sent_theme["% Négatif"],
            name="Négatif", orientation="h",
            marker_color=COLOR_ACCENT,
            text=sent_theme["% Négatif"].apply(lambda x: f"{x:.0f}%" if x > 5 else ""),
            textposition="inside",
        ))
        fig_sent.update_layout(
            barmode="stack",
            height=320,
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(range=[0, 100], ticksuffix="%", gridcolor="#F0F0F0"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_sent, use_container_width=True)

    st.markdown("---")
    st.markdown("### Nuage de mots par thème")
    st.caption("Termes les plus fréquents dans les avis — filtrable par thème et tonalité")

    col_wc1, col_wc2, col_wc3 = st.columns([2, 2, 2])
    with col_wc1:
        themes_wc = sorted(df["theme_display"].dropna().unique().tolist())
        theme_wc  = st.selectbox("Thème", themes_wc, key="wc_theme")
    with col_wc2:
        tonalite  = st.radio(
            "Tonalité",
            ["Tous", "Positifs", "Négatifs"],
            horizontal=True,
            key="wc_ton",
        )
    with col_wc3:
        camping_wc = st.selectbox(
            "Camping",
            ["Tous"] + sorted([c for c in df["nom_etablissement"].unique()
                               if c not in ("Marque_Globale", "Inconnu")]),
            key="wc_camping",
        )

    # Filtrage via sentiment_label
    df_wc = df[df["theme_display"] == theme_wc].copy()
    if tonalite == "Positifs" and df["sentiment_label"].notna().any():
        df_wc = df_wc[df_wc["sentiment_label"] == "Positif"]
    elif tonalite == "Négatifs" and df["sentiment_label"].notna().any():
        df_wc = df_wc[df_wc["sentiment_label"] == "Négatif"]
    if camping_wc != "Tous":
        df_wc = df_wc[df_wc["nom_etablissement"] == camping_wc]

    # Mots à exclure (stopwords + termes non informatifs)
    STOPWORDS = {
        "le", "la", "les", "un", "une", "des", "du", "de", "et", "en",
        "au", "aux", "que", "qui", "est", "pas", "sur", "par", "pour",
        "dans", "avec", "nous", "on", "il", "elle", "ils", "elles", "je",
        "se", "sa", "son", "ses", "ce", "cette", "ces", "ou", "mais",
        "donc", "car", "ni", "ne", "plus", "très", "bien", "tout", "aussi",
        "être", "avoir", "plus", "si", "comme", "lors", "notre", "nos",
        "huttopia", "camping", "séjour", "avis", "note", "commentaire",
        "nuits", "envoyé", "avec", "the", "and", "was", "for", "are",
        "very", "we", "had", "have", "been", "were", "our", "this",
    }

    if df_wc.empty:
        st.info(f"Aucun avis pour ce filtre ({theme_wc} / {tonalite}).")
    else:
        try:
            from wordcloud import WordCloud
            import matplotlib.pyplot as plt
            import re

            # Concatène tous les textes
            corpus = " ".join(df_wc["texte_propre"].dropna().astype(str).tolist())
            corpus = re.sub(r"[^\w\sàâäéèêëïîôùûüç'-]", " ", corpus.lower())

            # Couleur selon tonalité
            if tonalite == "Positifs":
                colormap = "Greens"
                bg = "#F0FFF4"
            elif tonalite == "Négatifs":
                colormap = "Reds"
                bg = "#FFF5F5"
            else:
                colormap = "YlGn"
                bg = "#F8F9FA"

            wc = WordCloud(
                width=900, height=380,
                background_color=bg,
                colormap=colormap,
                stopwords=STOPWORDS,
                max_words=80,
                min_word_length=4,
                collocations=False,
                prefer_horizontal=0.85,
            ).generate(corpus)

            fig_wc, ax = plt.subplots(figsize=(11, 4))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            fig_wc.patch.set_facecolor(bg)
            plt.tight_layout(pad=0)
            st.pyplot(fig_wc)
            plt.close(fig_wc)

            st.caption(
                f"{len(df_wc)} avis · thème **{theme_wc}** · "
                f"tonalité **{tonalite}**"
                + (f" · camping **{camping_wc}**" if camping_wc != "Tous" else "")
            )

        except ImportError:
            st.warning(
                "La librairie `wordcloud` n'est pas installée. "
                "Lance : `pip install wordcloud matplotlib`"
            )

    st.markdown("---")
    col_lang, col_verb = st.columns([1, 2])

    with col_lang:
        st.markdown("### Langues des avis")
        lang_counts = df["langue"].value_counts().reset_index()
        lang_counts.columns = ["Langue", "Nb avis"]
        lang_labels = {
            "fr": "🇫🇷 Français", "en": "🇬🇧 Anglais",
            "de": "🇩🇪 Allemand", "nl": "🇳🇱 Néerlandais",
            "es": "🇪🇸 Espagnol", "it": "🇮🇹 Italien",
        }
        lang_counts["Langue"] = lang_counts["Langue"].map(lang_labels).fillna(lang_counts["Langue"])

        fig4 = px.bar(
            lang_counts.head(8),
            x="Nb avis", y="Langue", orientation="h",
            color_discrete_sequence=[COLOR_PRIMARY],
            text="Nb avis",
        )
        fig4.update_traces(textposition="outside")
        fig4.update_layout(
            height=280, showlegend=False,
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=10, r=40, t=10, b=10),
            xaxis=dict(gridcolor="#F0F0F0"),
        )
        st.plotly_chart(fig4, use_container_width=True)

    with col_verb:
        st.markdown("### Verbatims clients")

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            themes_dispo = ["Tous"] + sorted(df["theme_display"].dropna().unique().tolist())
            filtre_theme = st.selectbox("Thème", themes_dispo)
        with col_f2:
            campings_dispo = ["Tous"] + sorted(
                [c for c in df["nom_etablissement"].unique()
                 if c not in ("Marque_Globale", "Inconnu")]
            )
            filtre_camping = st.selectbox("Camping", campings_dispo)
        with col_f3:
            sources_dispo = ["Toutes"] + sorted(df["source"].unique().tolist())
            filtre_source = st.selectbox("Source", sources_dispo)

        df_verb = df.copy()
        if filtre_theme != "Tous":
            df_verb = df_verb[df_verb["theme_display"] == filtre_theme]
        if filtre_camping != "Tous":
            df_verb = df_verb[df_verb["nom_etablissement"] == filtre_camping]
        if filtre_source != "Toutes":
            df_verb = df_verb[df_verb["source"] == filtre_source]

        df_verb = df_verb.sort_values("note_std", ascending=False).head(15)

        for _, row in df_verb.iterrows():
            texte = str(row["texte_propre"])[:300]
            note  = row["note_std"]
            emoji = "⭐" * int(round(note)) if pd.notna(note) else ""
            st.markdown(
                f'<div class="verbatim">'
                f'<span class="source-tag">{row["source"]} · {row["nom_etablissement"]}</span> '
                f'{emoji}<br>{texte}{"..." if len(str(row["texte_propre"])) > 300 else ""}'
                f'</div>',
                unsafe_allow_html=True,
            )


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main() -> None:
    # Header
    st.markdown(
        '<h1 style="margin-bottom:0">🏕️ Huttopia — Voice of Customer</h1>',
        unsafe_allow_html=True,
    )
    st.caption("Analyse automatisée des avis clients · Booking · Google Maps · Trustpilot")
    st.markdown("---")

    # Chargement
    if not DATA_PATH.exists():
        st.error(f"Fichier de données introuvable : `{DATA_PATH}`")
        st.info("Lance d'abord `python processing/data_merger.py` puis `python ml/topic_classification.py`")
        st.stop()

    df_raw = load_data()

    # Filtres sidebar
    df = sidebar_filters(df_raw)

    if df.empty:
        st.warning("Aucun avis ne correspond aux filtres sélectionnés.")
        st.stop()

    # Onglets
    tab1, tab2 = st.tabs(["📊 Vue Commerciale", "🎯 Vue Marketing"])

    with tab1:
        vue_commerciale(df)

    with tab2:
        vue_marketing(df)

    # Footer
    st.markdown("---")
    st.caption(
        f"Corpus : {len(df_raw)} avis analysés · "
        "Précision classification thématique : ~85% (validation manuelle 20 avis) · "
        "Projet portfolio — candidature Business Analyst Huttopia"
    )


if __name__ == "__main__":
    main()
