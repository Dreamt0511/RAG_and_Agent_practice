import psycopg
import os

DB_URL = os.getenv("user_DB_URL")

try:
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            # 1. 查看当前用户
            cur.execute("SELECT current_user;")
            current_user = cur.fetchone()[0]
            print(f"当前数据库用户: {current_user}")

            # 2. 查看会话用户和当前用户
            cur.execute("SELECT session_user, current_user;")
            session_user, curr_user = cur.fetchone()
            print(f"会话用户: {session_user}")
            print(f"当前用户: {curr_user}")

            # 3. 查看所有用户及其详细权限
            cur.execute("""
                SELECT 
                    usename as username,
                    usesuper as is_superuser,
                    usecreatedb as can_create_db
                FROM pg_user
                ORDER BY usename;
            """)
            users = cur.fetchall()
            print("\n所有数据库用户:")
            print("-" * 50)
            for user in users:
                print(f"  用户名: {user[0]}")
                print(f"    超级用户: {'✅' if user[1] else '❌'}")
                print(f"    可创建DB: {'✅' if user[2] else '❌'}")
                print()

            # 4. 查看当前用户在public模式上的权限
            cur.execute("""
                SELECT 
                    has_schema_privilege(current_user, 'public', 'CREATE') as can_create,
                    has_schema_privilege(current_user, 'public', 'USAGE') as can_use
            """)
            permissions = cur.fetchone()
            print(f"\n当前用户 '{current_user}' 在public模式上的权限:")
            print("-" * 50)
            print(f"  CREATE: {'✅' if permissions[0] else '❌'} (可以创建表)")
            print(f"  USAGE: {'✅' if permissions[1] else '❌'} (可以使用表)")

            # 5. 查看数据库级别的权限
            cur.execute("""
                SELECT 
                    has_database_privilege(current_user, current_database(), 'CONNECT') as can_connect,
                    has_database_privilege(current_user, current_database(), 'CREATE') as can_create
            """)
            db_perms = cur.fetchone()
            print(f"\n当前数据库 '{conn.info.dbname}' 的权限:")
            print("-" * 50)
            print(f"  CONNECT: {'✅' if db_perms[0] else '❌'} (可以连接)")
            print(f"  CREATE: {'✅' if db_perms[1] else '❌'} (可以创建数据库对象)")

            # 6. 查看用户拥有的表和可访问的表
            try:
                cur.execute("""
                    SELECT 
                        (SELECT count(*) FROM pg_tables WHERE tableowner = current_user) as owned_tables,
                        (SELECT count(*) FROM information_schema.tables 
                         WHERE table_schema = 'public') as total_tables
                """)
                summary = cur.fetchone()
                print(f"\n用户 '{current_user}' 权限总结:")
                print("-" * 50)
                print(f"  拥有的表数量: {summary[0]}")
                print(f"  public模式总表数: {summary[1]}")
            except Exception as e:
                print(f"\n查询表信息时出错: {e}")

            # 7. 判断用户类型
            cur.execute("SELECT usesuper FROM pg_user WHERE usename = current_user;")
            is_super = cur.fetchone()[0]
            if is_super:
                print("\n⚠️  当前用户是超级用户，拥有所有权限！")
            else:
                print("\nℹ️  当前用户是普通用户，但已有创建表的必要权限")

except Exception as e:
    print(f"连接失败: {e}")