from django.db import models


class ThinkContestMain(models.Model):
    """씽굿 분야별 공모전 페이지 테이블"""

    id = models.AutoField(primary_key=True)
    contest_name = models.CharField(max_length=128, verbose_name="공모명")
    contest_url = models.CharField(max_length=100, verbose_name="분야 url")
    sponsor = models.CharField(max_length=30, verbose_name="주최")
    # progressing = models.CharField(max_length=20, verbose_name="진행 사항")

    start_date = models.DateTimeField(verbose_name="대회 시작 일자")
    end_date = models.DateTimeField(verbose_name="대회 종료 일자")

    category = models.ForeignKey(
        to="ThinkContestCategories",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="카테고리 id",
    )

    class Meta:
        db_table = "thinkcontest_main"
        app_label = "contest"


class ThinkContestDetail(models.Model):
    """씽굿 공모전 세부 테이블"""

    id = models.AutoField(primary_key=True)

    main = models.ForeignKey(
        to="ThinkContestMain", on_delete=models.CASCADE, verbose_name="main id"
    )

    class Meta:
        db_table = "thinkcontest_detail"
        app_label = "contest"


class ThinkContestCategories(models.Model):
    """씽굿 공모전 분야 정보 테이블"""

    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=30, verbose_name="공모전 분야")
    urls = models.CharField(max_length=100, verbose_name="분야 url")

    class Meta:
        db_table = "thinkcontest_categories"
        app_label = "contest"
