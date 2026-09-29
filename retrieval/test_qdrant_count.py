from retrieval.qdrant_store import (
    COLLECTION_NAME,
    get_qdrant_client,
)


def main():
    client = get_qdrant_client()

    collection_info = client.get_collection(
        collection_name=COLLECTION_NAME
    )

    print("Qdrant collection verification successful.")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Points stored: {collection_info.points_count}")


if __name__ == "__main__":
    main()