# 以下を上書き
from rest_framework import viewsets
from .models import Code,CodeHeader,Tree
from .serializers import CodeHeaderSerializer,CodeSerializer
from django.db.models import Max
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .settings import DIGIT

class CodeHeaderView(viewsets.ModelViewSet):
    queryset = CodeHeader.objects.all()
    serializer_class = CodeHeaderSerializer


class CodeView(viewsets.ModelViewSet):
    queryset = Code.objects.all()
    serializer_class = CodeSerializer

    # コードの最大値を取得するメソッド
    @action(detail=False, methods=['post'])
    def maxCode(self, request):
        ch = request.POST.get('code_header_id')
        kind = request.POST.get('kind')


        # POST値の判定
        if ch != None and kind != None:

            # 英番号の最大値を取得
            ch_instance = Code.objects.filter(code_header=ch)
            en_max =ch_instance.aggregate(Max('en_number'))['en_number__max']
            maxdig = (10**DIGIT)-1 # 10*4-1 = 9999

            return_en_number=0
            return_max_number=0
            return_code_str:str=''
            code_obj={}

            # en_numberの最大値分ループ処理をする
            for i in range(en_max):
                # Aでの最大値、Bでの最大値、Cでの最大値・・・というように値を取得する
                value=Code.objects.filter(code_header=ch).filter(en_number=i+1).aggregate(Max('number'))['number__max']

                # x < 9999
                if(value < maxdig):
                    en_number = i + 1
                    return_en_number = en_number
                    return_max_number = value+1
                    return_code_str="{}-{}{}".format(CodeHeader.objects.get(pk=ch),
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
                        return_code_str="{}-{}{}".format(CodeHeader.objects.get(pk=ch),
                                                        chr(64+en_number),
                                                        str(return_max_number).zfill(DIGIT)
                                                        )
                        
                        code_obj = Code.objects.create(code_header=CodeHeader.objects.get(pk=ch),
                                                                en_number=return_en_number,
                                                                number=return_max_number,
                                                                kind=kind,
                                                                code=return_code_str
                                                                )
                        break
                elif(value == None):
                    return Response({'message': 'パラメータが不正です。'}, status=555)
            
            return Response({'code_id':code_obj.id,
                             'en_number': return_en_number,
                             'number':return_max_number,
                             'code':return_code_str,
                             'message':''
                             },
                            status=status.HTTP_200_OK)
        
        return Response({'message': 'パラメータが不足しています。'}, status=555)