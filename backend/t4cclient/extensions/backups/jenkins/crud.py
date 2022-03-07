import t4cclient.extensions.backups.jenkins.models as jenkins_schema
from sqlalchemy.orm import Session


def get_pipeline_of_model(
    db: Session, git_model_id: int
) -> jenkins_schema.DatabaseJenkinsPipeline:
    return (
        db.query(jenkins_schema.DatabaseJenkinsPipeline)
        .filter(jenkins_schema.DatabaseJenkinsPipeline.git_model_id == git_model_id)
        .first()
    )


def add_pipeline(
    db: Session, git_model_id: int, name: str
) -> jenkins_schema.DatabaseJenkinsPipeline:
    pipeline = jenkins_schema.DatabaseJenkinsPipeline(
        name=name, git_model_id=git_model_id
    )
    db.add(pipeline)
    db.commit()
    db.refresh(pipeline)
    return pipeline


def remove_pipeline(db: Session, id: int):
    db.query(jenkins_schema.DatabaseJenkinsPipeline).filter(
        jenkins_schema.DatabaseJenkinsPipeline.id == id
    ).delete()
    db.commit()


def remove_pipeline_by_name(db: Session, name: str):
    db.query(jenkins_schema.DatabaseJenkinsPipeline).filter(
        jenkins_schema.DatabaseJenkinsPipeline.name == name
    ).delete()
    db.commit()


def remove_pipeline_by_model_id(db: Session, model_id: str):
    db.query(jenkins_schema.DatabaseJenkinsPipeline).filter(
        jenkins_schema.DatabaseJenkinsPipeline.git_model_id == model_id
    ).delete()
    db.commit()
