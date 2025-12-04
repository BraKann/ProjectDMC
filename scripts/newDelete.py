#!/usr/bin/env python3
"""Script de suppression par batch pour Datastore (avec debug)"""
import sys
from google.cloud import datastore

def delete_all_entities():
    """Supprime toutes les entités Post et User par batch de 500"""
    
    print("="*60)
    print("🔍 Initialisation du client Datastore...")
    print("="*60)
    
    try:
        client = datastore.Client()
        print(f"✅ Client créé avec le projet : {client.project}")
    except Exception as e:
        print(f"❌ Erreur lors de la création du client : {e}")
        print("\n💡 Vérifiez que :")
        print("   1. GOOGLE_APPLICATION_CREDENTIALS est défini")
        print("   2. Vous êtes authentifié avec 'gcloud auth application-default login'")
        return
    
    # ==========================================
    # Suppression des Posts
    # ==========================================
    print("\n" + "="*60)
    print("🗑️  Suppression des Posts...")
    print("="*60)
    
    try:
        query = client.query(kind='Post')
        query.keys_only()
        
        print("📊 Récupération des clés Post...")
        posts_keys = list(query.fetch())
        total_posts = len(posts_keys)
        
        print(f"📌 Nombre de Posts trouvés : {total_posts}")
        
        if total_posts > 0:
            # Suppression par batch de 500
            deleted_count = 0
            for i in range(0, len(posts_keys), 500):
                batch = [entity.key for entity in posts_keys[i:i+500]]
                client.delete_multi(batch)
                deleted_count += len(batch)
                print(f"   ✓ Supprimés : {deleted_count}/{total_posts} posts")
            
            print(f"✅ {total_posts} posts supprimés.")
        else:
            print("ℹ️  Aucun post à supprimer.")
            
    except Exception as e:
        print(f"❌ Erreur lors de la suppression des Posts : {e}")
        import traceback
        traceback.print_exc()
    
    # ==========================================
    # Suppression des Users
    # ==========================================
    print("\n" + "="*60)
    print("🗑️  Suppression des Users...")
    print("="*60)
    
    try:
        query = client.query(kind='User')
        query.keys_only()
        
        print("📊 Récupération des clés User...")
        users_keys = list(query.fetch())
        total_users = len(users_keys)
        
        print(f"📌 Nombre de Users trouvés : {total_users}")
        
        if total_users > 0:
            # Suppression par batch de 500
            deleted_count = 0
            for i in range(0, len(users_keys), 500):
                batch = [entity.key for entity in users_keys[i:i+500]]
                client.delete_multi(batch)
                deleted_count += len(batch)
                print(f"   ✓ Supprimés : {deleted_count}/{total_users} users")
            
            print(f"✅ {total_users} users supprimés.")
        else:
            print("ℹ️  Aucun user à supprimer.")
            
    except Exception as e:
        print(f"❌ Erreur lors de la suppression des Users : {e}")
        import traceback
        traceback.print_exc()
    
    # ==========================================
    # Résumé final
    # ==========================================
    print("\n" + "="*60)
    print(f"🎉 Suppression terminée")
    print(f"   Posts supprimés : {total_posts if 'total_posts' in locals() else 0}")
    print(f"   Users supprimés : {total_users if 'total_users' in locals() else 0}")
    print("="*60)


if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════════════════════╗
║      SUPPRESSION COMPLÈTE DE LA BASE DATASTORE            ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    try:
        delete_all_entities()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)