// 회원가입 버튼 누르면 로그인 페이지 숨기기
function toggle_sign_up() {
    $("#input-username").val('')
    $("#input-password").val('')
    $("#sign-up-box").toggleClass("is-hidden")
    $("#div-sign-in-or-up").toggleClass("is-hidden")
    $("#btn-check-dup").toggleClass("is-hidden")
    $("#help-id").toggleClass("is-hidden")
    $("#help-password").toggleClass("is-hidden")
    $("#help-password2").toggleClass("is-hidden")
    $("#help-id-login").toggleClass("is-hidden")
    $("#help-password-login").toggleClass("is-hidden")
}

// 아이디, 비밀번호 형식 체크하기
function is_nickname(asValue) {
    var regExp = /^(?=.*[a-zA-Z])[-a-zA-Z0-9_.]{5,10}$/;
    return regExp.test(asValue);
}

function is_password(asValue) {
    var regExp = /^(?=.*\d)(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{8,20}$/;
    return regExp.test(asValue);
}

// 회원가입 아이디 중복 확인 함수
function check_dup() {
    let username = $("#input-username").val()
    if (username == "") {
        $("#help-id").text("아이디를 입력해주세요.").removeClass("is-safe").addClass("is-danger")
        $("#input-username").focus()
        return;
    }
    if (!is_nickname(username)) {
        $("#help-id").text("영문자로 시작하는 영문자 또는 숫자 5~8자").removeClass("is-safe").addClass("is-danger")
        $("#input-username").focus()
        return;
    }
    $("#help-id").addClass("is-loading")
    $.ajax({
        type: "POST",
        url: "/sign_up/check_dup",
        data: {
            username_give: username
        },
        success: function (response) {
            if (response["exists"]) {
                $("#help-id").text("이미 존재하는 아이디입니다.").removeClass("is-safe").addClass("is-danger")
                $("#input-username").focus()
            } else {
                $("#help-id").text("사용할 수 있는 아이디입니다.").removeClass("is-danger").addClass("is-success")
            }
            $("#help-id").removeClass("is-loading")
        }
    });
}

// 닉네임
// function is_nick(asValue) {
//     const regex = /^[ㄱ-ㅎ|가-힣|a-z|A-Z|0-9|]+$/;
//     return regex.test(asValue)
// }

// 닉네임 중복
// function check_dup_nick() {
//     let usernick = $("#input-nickname").val()
//     console.log(usernick)
//     if (usernick == "") {
//         $("#help-nick").text("닉네임을 입력해주세요.").removeClass("is-safe").addClass("is-danger")
//         $("#input-usernick").focus()
//         return;
//     }
//     if (!is_nick(usernick)) {
//         $("#help-nick").text("닉네임의 형식을 확인해주세요. 특수문자 제외 한글, 영문, 숫자").removeClass("is-safe").addClass("is-danger")
//         $("#input-username").focus()
//         return;
//     }
//     $("#help-nick").text("사용할 수 있는 닉네임입니다.").removeClass("is-danger").addClass("is-success")
// }

// 회원가입 완료하기 함수, 아이디 확인, 비밀번호 확인, 로그인 페이지로 이동
function sign_up() {
    let username = $("#input-username").val()
    let password = $("#input-password").val()
    let password2 = $("#input-password2").val()

    // 아이디 다시 확인하기
    if ($("#help-id").hasClass("is-danger")) {
        alert("아이디를 다시 확인해주세요.")
        return;
    } else if (!$("#help-id").hasClass("is-success")) {
        alert("아이디 중복확인을 해주세요.")
        return;
    }

    // 비밀 번호 확인하기
    if (password == "") {
        $("#help-password").text("비밀번호를 입력해주세요.").removeClass("is-safe").addClass("is-danger")
        $("#input-password").focus()
        return;
    } else if (!is_password(password)) {
        $("#help-password").text("비밀번호의 형식을 확인해주세요. 영문과 숫자 필수 포함, 특수문자(!@#$%^&*) 사용가능 8-20자").removeClass("is-safe").addClass("is-danger")
        $("#input-password").focus()
        return
    } else {
        $("#help-password").text("사용할 수 있는 비밀번호입니다.").removeClass("is-danger").addClass("is-success")
    }
    if (password2 == "") {
        $("#help-password2").text("비밀번호를 입력해주세요.").removeClass("is-safe").addClass("is-danger")
        $("#input-password2").focus()
        return;
    } else if (password2 != password) {
        $("#help-password2").text("비밀번호가 일치하지 않습니다.").removeClass("is-safe").addClass("is-danger")
        $("#input-password2").focus()
        return;
    } else {
        $("#help-password2").text("비밀번호가 일치합니다.").removeClass("is-danger").addClass("is-success")
    }

    $.ajax({
        type: "POST",
        url: "/sign_up/save",
        data: {
            username: username,
            password: password
        },
        success: function (response) {
            alert("회원가입을 축하드립니다!")
            window.location.replace("/login")
        }
    });

}

// 쿠키 받고 로그인 하기, 메인 페이지로 넘어가기
function sign_in() {
    let username = $("#input-username").val()
    let password = $("#input-password").val()

    if (username == "") {
        $("#help-id-login").text("아이디를 입력해주세요.")
        $("#input-username").focus()
        return;
    } else {
        $("#help-id-login").text("")
    }

    if (password == "") {
        $("#help-password-login").text("비밀번호를 입력해주세요.")
        $("#input-password").focus()
        return;
    } else {
        $("#help-password-login").text("")
    }

    $.ajax({
        type: "POST",
        url: "/sign_in",
        data: {
            username: username,
            password: password
        },
        success: function (response) {
            if (response['result'] == 'success') {
                $.cookie('mytoken', response['token'], {path: '/'});
                window.location.replace("/main")
            } else {
                alert(response['msg'])
            }
        }
    });

}