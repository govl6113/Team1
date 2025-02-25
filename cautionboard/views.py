from django.shortcuts import redirect, render, get_object_or_404
from .models import Comment
from .models import Text
from django.utils import timezone
from django.contrib import messages


def home(request):
    return render(request, "home.html")


menu_bar = []
type = []
# detail함수 : home에서 입력한 각각의 코스들이 DB의 Text Table에 있는지 조회하고 detail.html에 띄워줌
def detail(request):
    trips = []  # home.html에서 입력한 코스들을 저장할 리스트
    trips.append(request.GET["start"])  # 리스트에 출발지 추가
    trips += request.GET.getlist("middle")  # 리스트에 경유지들 추가
    trips.append(request.GET["end"])  # 리스트에 도착지 추가

    type.clear()

    if request.GET["애완견 여부"] == "yes":
        type.append(True)
    else:
        type.append(False)

    type.append(request.GET["여행 종류"])
    print(type)

    menu_bar.clear()

    if "" in trips or " " in trips:  # 홈에서 공란으로 제출한 코스가 있다면
        messages.warning(request, "! 계획한 여행코스를 빠짐없이 입력해주세요 !")
        return redirect("home")
    else:  # 홈에서 모든 코스를 적어서 제출(즉 정상적인 케이스)
        for place_name in trips:  # home에서 입력한 각 코스들에 대해 반복문 실행
            menu = []  # menu = 각 코스의 1)'장소명'과 2)'그 장소에 대한 설명'을 담을 리스트
            menu.append(place_name)  # 그 장소의 장소명을 추가, 이제 장소에 대한 설명만 담으면 됨.
            try:  # Text table에 해당 코스가 있는지 없는지 검사
                s = Text.objects.get(pk=place_name)
            except Text.DoesNotExist:  # Text table에 해당 코스가 없으면 대체 문구로 대체
                menu.append("대체 문구")
            else:  # Text table에 해당 코스가 있으면 그 코스의 설명을 가져옴
                menu.append(s.summary())
            finally:
                menu_bar.append(menu)
                # menu_bar의 형태 : ex) [["출발지", "출발지에 대한 설명"], ["경유지", "경유지에 대한 설명"], ["도착지", "도착지에 대한 설명"]]
        return render(request, "detail.html", {"trip_list": menu_bar})


# place에 해당하는 comments들을 가져옴
def getplacedetails(request, place):
    comments = Comment.objects.filter(place=place)
    truecomments = (
        comments.filter(pet=type[0]).filter(tripType=type[1]).order_by("-yes")
    )

    try:  # Text table에 있는 장소면
        text = Text.objects.get(pk=place)
    except Text.DoesNotExist:  # Text table에 없는 장소면 DoesNotExist오류 발생, 이 때에 대한 처리
        text = {}

    comment_list = list(comments)
    truecomments_list = list(truecomments)
    falsecomments_list = [x for x in comment_list if x not in truecomments_list]
    falsecomments_list.sort(key=lambda Comment: Comment.yes, reverse=True)
    # comment2_list=list(comments2)
    comment_list.clear()
    comment_list += truecomments_list + falsecomments_list
    # comment_list.sort(key=lambda Comment: Comment.yes,reverse=True)

    return render(
        request,
        "detail_detail.html",
        {"trip_list": menu_bar, "comment_list": comment_list, "text": text},
    )


# 주의사항 더하기
def addcaution(request, place):
    comment = Comment()
    comment.author = request.POST.get("author", False)
    comment.place = Text.objects.get(pk=place)
    comment.caution = request.POST.get("caution", False)
    if request.POST.get("have-pet", False) == "yes":
        comment.pet = True
    else:
        comment.pet = False
    comment.tripType = request.POST.get("trip-type", False)
    comment.pub_date = timezone.datetime.now()
    comment.save()

    return redirect("detail_detail", place)


def yesUp(request, place, id):
    yesupcomment = get_object_or_404(Comment, id=id)
    # if yesupcomment.yes.filter(id = id).exists():
    yesupcomment.yes += 1
    yesupcomment.save()
    return redirect("detail_detail", place)


def noUp(request, place, id):
    noupcomment = get_object_or_404(Comment, id=id)
    # if yesupcomment.yes.filter(id = id).exists():
    noupcomment.no += 1
    noupcomment.save()
    return redirect("detail_detail", place)
