from .base_objects import *
from .sde_importer import sde_impoter


class Locations(dec_Base.Base,table_row,sde_impoter):
    __tablename__ = 'locations'

    location_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    name = Column(String,default=None,nullable=True)
    typeID = Column(Integer,ForeignKey("types.type_id"),nullable=True)
    groupID = Column(Integer,ForeignKey("groups.group_id"),nullable=True)
    pos_x = Column(Float,default=None,nullable=True)
    pos_y = Column(Float, default=None, nullable=True)
    pos_z = Column(Float, default=None, nullable=True)
    radius = Column(Float,default=None,nullable=True)

    object_kills_at_location = relationship("Kills",uselist=True,back_populates="object_location")
    object_type = relationship("Types",uselist=False,lazy="joined")
    object_group = relationship("Groups",uselist=False,lazy="joined")

    def __init__(self, eve_id: int):
        self.location_id = eve_id

    def get_id(self):
        return self.location_id

    @classmethod
    def primary_key_row(cls):
        return cls.location_id

    @classmethod
    def make_from_sde(cls,__row):
        new_row = cls(__row.itemID)
        new_row.name = __row.itemName
        new_row.typeID = __row.typeID
        new_row.groupID = __row.groupID
        new_row.pos_x = __row.x
        new_row.pos_y = __row.y
        new_row.pos_z = __row.z
        new_row.radius = __row.radius
        return new_row

    @classmethod
    def get_missing_ids(cls, service_module, sde_session, sde_base):
        existing_ids = [i.location_id for i in
                        service_module.get_session().query(cls.location_id).all()]
        importing_ids = [i.itemID for i in sde_session.query(sde_base.itemID).all()]
        return list(set(importing_ids) - set(existing_ids))

    @classmethod
    def import_stargates(cls, service_module, sde_session, sde_base):
        db: Session = service_module.get_session()
        try:
            missing_items = db.query(cls).filter(cls.name == None).all()
            length_missing_ids = len(missing_items)
            if length_missing_ids > 0:
                print("Need to import stargate names for {} {}".format(str(length_missing_ids), cls.__name__))
            else:
                return
            for chunk in name_only.split_lists(missing_items, 75000):
                start = datetime.datetime.utcnow()
                try:
                    for item in chunk:
                        try:
                            __row = sde_session.query(sde_base).filter(sde_base.itemID == item.location_id).one()
                            item.name = __row.itemName
                            db.merge(item)
                        except Exception as ex:
                            print(ex)
                    db.commit()
                    print("Imported {} {} from the SDE in {} seconds".format(str(len(chunk)), cls.__name__, str(
                        (datetime.datetime.utcnow() - start).total_seconds())))
                except Exception as ex:
                    print(ex)
                    db.rollback()
        except Exception as ex:
            print(ex)
            db.rollback()
            sde_session.rollback()
        finally:
            db.close()
            sde_session.close()

    @classmethod
    def get_query_filter(cls, sde_base):
        return sde_base.itemID

    @classmethod
    def row_action(cls,row,db_session):
        db_session.add(row)


from . import types,groups