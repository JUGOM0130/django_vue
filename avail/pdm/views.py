# 以下を上書き
from rest_framework import viewsets
from .models import Code,CodeHeader,Tree
from .serializers import CodeHeaderSerializer,CodeSerializer
from django.db.models import Max
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .settings import DIGIT

# 定数定義
KUMI = '1'
BUHIN = '2'
KOUNYUUHIN = '3'
Z = 26

class CodeHeaderView(viewsets.ModelViewSet):
    queryset = CodeHeader.objects.all()
    serializer_class = CodeHeaderSerializer
    """
    http://127.0.0.1:8000/api/codeheader        GET     全件取得
    http://127.0.0.1:8000/api/codeheader/id/    GET     詳細
    http://127.0.0.1:8000/api/codeheader/       POST    作成
    http://127.0.0.1:8000/api/codeheader/id/    PUT     更新
    http://127.0.0.1:8000/api/codeheader/id/    PATCH   部分更新
    http://127.0.0.1:8000/api/codeheader/id/    DELETE  削除

    """

class CodeView(viewsets.ModelViewSet):
    queryset = Code.objects.all()
    serializer_class = CodeSerializer

    # コードの最大値を取得するメソッド
    @action(detail=False, methods=['post'])
    def maxCode(self, request):
        # ch = request.POST.get('code_header_id')
        ch = request.POST.get('code_header')
        kind = request.POST.get('kind')

        # POST値の判定
        if ch != None and kind != None and ch != '' and kind != '':
            
            # 英番号の最大値を取得
            ch_instance = Code.objects.filter(kind=kind).filter(code_header=ch)
            en_max = ch_instance.aggregate(Max('en_number'))['en_number__max']
            maxdig = (10**DIGIT)-1 # 10*4-1 = 9999

            return_en_number=0
            return_max_number=0
            return_code_str:str=''
            code_obj={}


    

            # 3項演算子の書き方
            # データがない場合は「１」をセット
            en_max = 1 if en_max == None or en_max == 0 else en_max
            




            # en_numberの最大値分ループ処理をする
            for i in range(en_max):
                # Aでの最大値、Bでの最大値、Cでの最大値・・・というように値を取得する
                value=Code.objects.filter(kind=kind).filter(code_header=ch).filter(en_number=i+1).aggregate(Max('number'))['number__max']

                


                # 三項演算子の書き方
                # 英番の連番未登録の場合「１」をセット（A0000の場合）
                value = 0 if value == None else value

                # x < 9999
                if(value < maxdig):
                    en_number = i + 1
                    return_en_number = en_number
                    return_max_number = value + 1
                    return_code_str = ""
                    
                    # ALD-A0001Z0 フォーマットの場合
                    if kind == KUMI: 
                        return_code_str="{}-{}{}".format(CodeHeader.objects.get(pk=ch),
                                                    chr(64+en_number),
                                                    str(return_max_number).zfill(DIGIT))
                    # ALD-AA0001Z0 フォーマットの場合
                    elif kind == BUHIN:
                        left_digit = int(en_number / 26) + 1
                        right_digit = (en_number % 26)
                        return_code_str="{}-{}{}".format(CodeHeader.objects.get(pk=ch),
                                                    chr(64+left_digit)+chr(64+right_digit),
                                                    str(return_max_number).zfill(DIGIT))
                        
                    # AL-A0001Z0 フォーマットの場合
                    elif kind == KOUNYUUHIN:
                        return_code_str="{}-{}{}Z0".format(CodeHeader.objects.get(pk=ch),
                                                    chr(64+en_number),
                                                    str(return_max_number).zfill(DIGIT))
                        

                    code_obj = Code.objects.create(code_header=CodeHeader.objects.get(pk=ch),
                                        en_number=en_number,
                                        number=return_max_number,
                                        kind=kind,
                                        code=return_code_str
                                        )
                    break

                # x == 9999
                elif(value == maxdig):
                    # 英語番号の最終ループか判定
                    if((i+1) == en_max):
                        # 最終ループのため、採番値をインクリメントしてインサート
                        # en_max + 1
                        # number 1
                        # をinsert
                        en_number = i + 2
                        return_en_number = en_number
                        return_max_number = 1
                        return_code_str = ""
                        
                        if kind == KUMI:
                            return_code_str="{}-{}{}".format(CodeHeader.objects.get(pk=ch),
                                                        chr(64+en_number),
                                                        str(return_max_number).zfill(DIGIT)
                                                        )
                        elif kind == BUHIN:
                            left_digit = int(en_number / 26) + 1
                            right_digit = (en_number % 26)
                            return_code_str="{}-{}{}".format(CodeHeader.objects.get(pk=ch),
                                                        chr(64+left_digit)+chr(64+right_digit),
                                                        str(return_max_number).zfill(DIGIT)
                                                        )
                        elif kind == KOUNYUUHIN:
                            return_code_str="{}-{}{}Z0".format(CodeHeader.objects.get(pk=ch),
                                                        chr(64+en_number),
                                                        str(return_max_number).zfill(DIGIT)
                                                        )
                        
                        # 英番が「Z」(26)より大きくなってしまった場合エラーを返す
                        if return_en_number == Z + 1:
                            return Response(
                                {
                                'message': '英番が振り切れました。\n桁を増やすか、管理者へ連絡してください。'
                                }, status=556)
                        
                        code_obj = Code.objects.create(code_header=CodeHeader.objects.get(pk=ch),
                                                                en_number=return_en_number,
                                                                number=return_max_number,
                                                                kind=kind,
                                                                code=return_code_str
                                                                )
                        break
                elif(value == None):
                    return Response({'message': 'パラメータが不正です。'}, status=554)


            return Response({'code_id':code_obj.id,
                        'en_number': return_en_number,
                        'number':return_max_number,
                        'code':return_code_str,
                        'message':''
                        },
                        status=status.HTTP_200_OK)

        return Response({'message': 'パラメータが不足しています。'}, status=555)


