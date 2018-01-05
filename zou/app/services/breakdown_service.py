from sqlalchemy import desc

from zou.app.models.asset_instance import AssetInstance
from zou.app.models.entity import Entity, EntityLink

from zou.app.services import shots_service, entities_service


def get_casting(shot_id):
    casting = []
    links = EntityLink.get_all_by(entity_in_id=shot_id)
    for link in links:
        casting.append({
            "asset_id": str(link.entity_out_id),
            "nb_occurences": link.nb_occurences
        })
    return casting


def update_casting(shot_id, casting):
    shot = shots_service.get_shot_raw(shot_id)
    shot.update({"entities_out": []})
    for cast in casting:
        EntityLink.create(
            entity_in_id=shot.id,
            entity_out_id=cast["asset_id"],
            nb_occurences=cast["nb_occurences"]
        )
    shot = Entity.get(shot.id)
    return casting


def get_asset_instances_for_entity(entity_id):
    instances = AssetInstance.query \
        .filter(AssetInstance.entity_id == entity_id) \
        .order_by(AssetInstance.asset_id, AssetInstance.number) \
        .all()

    result = {}
    for instance in instances:
        asset_id = str(instance.asset_id)
        if asset_id not in result:
            result[asset_id] = []
        result[asset_id].append(instance.serialize())
    return result


def get_entity_asset_instances_for_asset(asset_id, entity_type_id):
    instances = AssetInstance.query \
        .filter(AssetInstance.asset_id == asset_id) \
        .filter(AssetInstance.entity_type_id == entity_type_id) \
        .order_by(AssetInstance.entity_id, AssetInstance.number) \
        .all()

    result = {}
    for instance in instances:
        entity_id = str(instance.entity_id)
        if entity_id not in result:
            result[entity_id] = []
        result[entity_id].append(instance.serialize())
    return result


def add_asset_instance_to_entity(entity_id, asset_id, description=""):
    entity = entities_service.get_entity_raw(entity_id)
    instance = AssetInstance.query \
        .filter(AssetInstance.entity_type_id == entity.entity_type_id) \
        .filter(AssetInstance.entity_id == entity_id) \
        .filter(AssetInstance.asset_id == asset_id) \
        .order_by(desc(AssetInstance.number)) \
        .first()

    number = 1
    if instance is not None:
        number = instance.number + 1

    return AssetInstance.create(
        asset_id=asset_id,
        entity_id=entity_id,
        entity_type_id=entity.entity_type_id,
        number=number,
        description=description
    ).serialize()


def get_asset_instances_for_shot(shot_id):
    return get_asset_instances_for_entity(shot_id)


def get_shot_asset_instances_for_asset(asset_id):
    return get_entity_asset_instances_for_asset(
        asset_id,
        shots_service.get_shot_type()["id"]
    )


def add_asset_instance_to_shot(shot_id, asset_id, description=""):
    return add_asset_instance_to_entity(shot_id, asset_id, description)


def get_asset_instances_for_scene(scene_id):
    return get_asset_instances_for_entity(scene_id)


def get_scene_asset_instances_for_asset(asset_id):
    return get_entity_asset_instances_for_asset(
        asset_id,
        shots_service.get_scene_type()["id"]
    )


def add_asset_instance_to_scene(scene_id, asset_id, description=""):
    return add_asset_instance_to_entity(scene_id, asset_id, description)
