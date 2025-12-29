import streamlit as st
import json
import os
import uuid

# ----------------------------
# Configuration
# ----------------------------
st.set_page_config(
    page_title="CampusAide - Aide entre étudiants",
    page_icon="🧑‍🎓",
    layout="centered"
)

DATA_FILE = "profiles.json"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_profiles():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_profiles(profiles):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)

if "profiles" not in st.session_state:
    st.session_state.profiles = load_profiles()

# ----------------------------
# Style CSS
# ----------------------------
st.markdown("""
<style>
.app-header {
    background: linear-gradient(120deg, #4e79f2, #2a4bc8);
    padding: 20px;
    border-radius: 12px;
    color: white;
    text-align: center;
    margin-bottom: 24px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.app-header h1 {
    margin: 0;
    font-size: 28px;
}
.app-header p {
    margin: 8px 0 0;
    opacity: 0.9;
    font-size: 16px;
}
.profile-card {
    background-color: #f9f9ff;
    border-left: 4px solid #4e79f2;
    padding: 16px;
    border-radius: 10px;
    margin-bottom: 16px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}
.stButton>button {
    background-color: #4e79f2;
    color: white;
    border-radius: 8px;
    font-weight: bold;
}
.stButton>button:hover {
    background-color: #3a5bc7;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Bannière
# ----------------------------
st.markdown("""
<div class="app-header">
    <h1>🧑‍🎓 CampusAide</h1>
    <p>« Ensemble, transformons chaque étudiant en une ressource pour la communauté ! »</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# Navigation
# ----------------------------
menu = ["🏠 Accueil", "📝 Créer mon profil", "🔍 Trouver de l’aide"]
choice = st.sidebar.selectbox("Navigation", menu)

# ----------------------------
# Page : Accueil
# ----------------------------
if choice == "🏠 Accueil":
    st.subheader("Bienvenue sur CampusAide !")
    profiles = list(st.session_state.profiles.values())
    total_competences = set(comp for p in profiles for comp in p.get("competences", []))
    
    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Étudiants inscrits", len(profiles))
    col2.metric("💡 Compétences partagées", len(total_competences))
    col3.metric("⭐ Note moyenne", f"{sum(p.get('rating', 0) for p in profiles)/len(profiles):.1f}" if profiles else "0.0")
    
    st.write("""
    CampusAide est une plateforme **solidaire et étudiante** qui te permet :
    - De **proposer ton aide** dans les matières que tu maîtrises,
    - De **trouver du soutien** quand tu en as besoin,
    - De **créer des liens**, apprendre ensemble, et même générer de petits revenus.
    
    💡 **Chaque talent compte. Chaque besoin mérite une réponse.**
    """)
    st.info("➡️ Commence par créer ton profil ou explore les étudiants disponibles !")

# ----------------------------
# Page : Créer mon profil
# ----------------------------
elif choice == "📝 Créer mon profil":
    st.title("✏️ Mon Profil Étudiant")
    
    with st.form("profile_form"):
        nom = st.text_input("Nom complet", placeholder="Ex: Boulagouaz Sanae")
        etablissement = st.text_input("Établissement", placeholder="Ex: Faculté des Sciences Dhar El Mahraz, Fès")
        filiere = st.text_input("Filière / Niveau", placeholder="Ex: Master BIG DATA ET SYSTEME INTELLIGENT")
        competences = st.text_input("Compétences (séparées par des virgules)", placeholder="Ex: Python, Maths, Anglais")
        
        # ✅ NOUVEAU : Modes de disponibilité
        mode_dispo = st.multiselect(
            "Modes de tutorat disponibles",
            ["En ligne", "Présentiel"],
            default=["En ligne"]
        )
        
        disponibilites = st.text_area("Vos plages de disponibilité", placeholder="Ex: Lundi 18h-20h, Mercredi après-midi")
        
        # ✅ NOUVEAU : Numéro de téléphone
        telephone = st.text_input("Numéro de téléphone (optionnel)", placeholder="Ex: 06 12 34 56 78")
        
        # ✅ NOUVEAU : Photo de profil
        photo = st.file_uploader("Photo de profil (optionnel)", type=["jpg", "jpeg", "png"])
        
        type_aide = st.radio("Type d’aide que je propose", ("Gratuit", "Rémunéré", "Échange de services"))
        solidarite = st.checkbox("❤️ Je souhaite prioritairement aider les étudiants en situation de précarité")
        
        submitted = st.form_submit_button("Publier mon profil")
        
        if submitted:
            if not nom or not competences:
                st.error("Veuillez remplir au moins votre nom et vos compétences.")
            else:
                photo_filename = None
                if photo is not None:
                    photo_filename = f"profile_{str(uuid.uuid4())}_{photo.name}"
                    with open(os.path.join(UPLOAD_FOLDER, photo_filename), "wb") as f:
                        f.write(photo.getbuffer())
                
                new_profile = {
                    "id": str(uuid.uuid4()),
                    "nom": nom,
                    "etablissement": etablissement,
                    "filiere": filiere,
                    "competences": [c.strip() for c in competences.split(",")],
                    "mode_dispo": mode_dispo,
                    "disponibilites": disponibilites,
                    "telephone": telephone,
                    "photo": photo_filename,
                    "type_aide": type_aide,
                    "solidarite": solidarite,
                    "rating": 0,
                    "review_count": 0
                }
                st.session_state.profiles[new_profile["id"]] = new_profile
                save_profiles(st.session_state.profiles)
                st.success("✅ Profil publié avec succès !")

    # Fiche de compétences
    st.markdown("---")
    st.subheader("🖨️ Générer ma fiche de compétences")
    if st.button("📝 Exporter en .txt"):
        if nom and competences:
            mode_txt = ', '.join(mode_dispo) if 'mode_dispo' in locals() else 'Non spécifié'
            fiche = f"""FICHE ÉTUDIANTE – CampusAide
============================
Nom : {nom}
Établissement : {etablissement}
Filière : {filiere}
Compétences : {competences}
Disponibilités : {disponibilites or 'Non précisées'}
Mode(s) : {mode_txt}
Téléphone : {'Fourni' if telephone else 'Non fourni'}
Type d’aide : {type_aide}
Solidarité : {'Oui' if solidarite else 'Non'}
"""
            st.code(fiche, language="text")
            st.download_button("⬇️ Télécharger en .txt", fiche, file_name="ma_fiche_campusAide.txt")
        else:
            st.warning("Veuillez remplir les champs obligatoires.")

# ----------------------------
# Page : Trouver de l’aide
# ----------------------------
elif choice == "🔍 Trouver de l’aide":
    st.title("🔎 Trouver un étudiant")
    
    search_term = st.text_input("Rechercher par compétence (ex: Python, Maths)", "").lower().strip()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        mode_filtrer = st.selectbox("Type d’aide", ["Tous", "Gratuit", "Rémunéré", "Échange de services"])
    with col2:
        tri = st.selectbox("Trier par", ["Pertinence", "Nom", "Note", "Récents"])
    with col3:
        solidarite_seulement = st.checkbox("❤️ Mode solidarité uniquement")
    
    profiles = list(st.session_state.profiles.values())
    filtered = profiles.copy()
    
    if search_term:
        filtered = [p for p in filtered if any(search_term in comp.lower() for comp in p.get("competences", []))]
    if mode_filtrer != "Tous":
        filtered = [p for p in filtered if p["type_aide"] == mode_filtrer]
    if solidarite_seulement:
        filtered = [p for p in filtered if p.get("solidarite", False)]
    
    base_order = {k: i for i, (k, v) in enumerate(st.session_state.profiles.items())}
    if tri == "Nom":
        filtered = sorted(filtered, key=lambda x: x["nom"])
    elif tri == "Note":
        filtered = sorted(filtered, key=lambda x: x.get("rating", 0), reverse=True)
    elif tri == "Récents":
        filtered = sorted(filtered, key=lambda x: base_order.get(x["id"], 0), reverse=True)
    elif tri == "Pertinence":
        filtered = sorted(filtered, key=lambda x: (-x.get("rating", 0), -base_order.get(x["id"], 0)))
    
    if not filtered:
        st.warning("Aucun étudiant trouvé." if search_term else "Aucun profil publié.")
    else:
        if not search_term:
            st.info("💡 Voici les profils les plus pertinents selon la communauté.")
        else:
            st.success(f"✅ {len(filtered)} profil(s) trouvé(s) pour '{search_term}'.")
        
        for p in filtered:
            with st.container():
                st.markdown('<div class="profile-card">', unsafe_allow_html=True)
                
                # Affichage photo
                photo_path = p.get("photo")
                if photo_path and os.path.exists(os.path.join(UPLOAD_FOLDER, photo_path)):
                    st.image(os.path.join(UPLOAD_FOLDER, photo_path), width=80)
                else:
                    st.markdown("👤")
                
                rating = p.get("rating", 0)
                count = p.get("review_count", 0)
                rating_display = f"⭐ {rating:.1f}" if count > 0 else "Pas encore noté"
                
                st.markdown(f"### {p['nom']} {'❤️' if p.get('solidarite') else ''}")
                st.markdown(f"**{p['filiere']}** – {p['etablissement']}")
                st.markdown(f"**Compétences** : {', '.join(p['competences'])}")
                st.markdown(f"**Disponibilités** : {p['disponibilites'] or 'Non précisées'}")
                st.markdown(f"**Mode(s)** : {', '.join(p.get('mode_dispo', ['Non spécifié']))}")
                st.markdown(f"**Type d’aide** : {p['type_aide']}")
                st.markdown(f"**Note** : {rating_display}")
                
                # Contact sécurisé
                if st.button("📩 Contacter", key=f"contact_{p['id']}"):
                    if p.get("telephone"):
                        st.info(f"📞 Numéro partagé : {p['telephone']}")
                    else:
                        st.info("📧 Contactez via email universitaire.")
                
                # Avis
                with st.expander("📝 Donner un avis"):
                    note = st.slider("Votre note", 1, 5, 5, key=f"slider_{p['id']}")
                    if st.button("Envoyer l’avis", key=f"btn_{p['id']}"):
                        old_rating = p.get("rating", 0)
                        old_count = p.get("review_count", 0)
                        new_count = old_count + 1
                        new_rating = (old_rating * old_count + note) / new_count
                        p["rating"] = new_rating
                        p["review_count"] = new_count
                        st.session_state.profiles[p["id"]] = p
                        save_profiles(st.session_state.profiles)
                        st.success("Merci pour votre retour !")
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.divider()