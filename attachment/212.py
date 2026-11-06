from pathlib import Path
import json,sqlite3,csv,re
R=Path(__file__).resolve().parent;B=R.parents[1]
a=json.loads((R/'cozy_coding.json').read_text());by={x['id']:x for x in a}
def nums(s):return [int(v) for v in s.split()]
excluded=nums('3913 3917 3927 3929 3933 3959 3964 3969 3999 4004 4007 4017 4018 4019 4022 4032 4034 4036 4037 4041 4043 4044 4045 4047 4048 3491 3661 3159')
# Reviewed language: distinguish the product's outcome from prior sleep problems,
# negated complaints, comparisons with another blanket, and merely possible issues.
cool_negative=nums('2629 2633 2636 2651 2695 2702 2722 2723 2725 2727 2750 2762 2763 2773 2782 2788 2803 2804 2810 2819 2845 2925 2938 2947 2960 3067 3068 3073 3080 3091 3092 3104 3107 3109 3119 3120 3126 3139 3145 3154 3171 3180 3186 3187 3192 3201 3206 3219 3226 3227 3244 3251 3260 3263 3264 3277 3305 3306 3338 3348 3383 3396 3398 3412 3443 3447 3459 3461 3463 3471 3474 3478 3480 3517 3522 3527 3535 3557 3563 3583 3610 3616 3625 3666 3667 3676 3677 3687 3692 3716 3746 3761 3792 3797 3808 3824 3828 3837 3843 3850 3925 3930 3991 3996 4000 4009 4029 4031 4035 4059 4071 2970 3090 3124 3600 3655 4053 2837 2853 3234 3238 3638 3415 3428 4061')
for x in a:
 x['negative']=[k for k in x['negative'] if k!='cool']
 if x['id'] in cool_negative:x['negative'].append('cool')
 if re.search(r"(?:not |won.t be |will not be |did not |didn.t |wasn.t )disappoint|can(?:not| not|.t) recommend.{0,30}enough",x['body']+' '+x['title'],re.I):x['negative']=[k for k in x['negative'] if k!='general']
def remove(key,ids,val='negative'):
 for i in nums(ids):by[i][val]=[k for k in by[i][val] if k!=key]
remove('quality','2858 3396 3438 3582 3583 3755 3803 3975 4033 3480')
remove('soft','2762 2928 3264 3317 3425 3563 3597 4033')
remove('weight','3151 3463 3500 3546 3814 3853 3859 4062 4085')
remove('slip','3239 3452 3656 3858 4028')
remove('fit','3073');remove('care','3649');remove('color','3498 3813');remove('odor','4097')
remove('general','3313 3674 3699 3870 3963 4063')
def add(ids,pos='',neg=''):
 for i in nums(ids):
  by[i]['positive']=sorted(set(by[i]['positive'])|set(pos.split()))
  by[i]['negative']=sorted(set(by[i]['negative'])|set(neg.split()))
add('2641 2647 2666 2676 2696 2710 2717 2721 2728 2737 2787 2820 2823 2833 2842 2851 2882 2902 2903 2935 2940 2945 2950 2982 3000 3004 3012 3030 3046 3051 3059 3129 3141 3149 3156 3168 3182 3183 3195 3208 3211 3261 3290 3292 3293 3353 3360 3378 3391 3395 3399 3420 3454 3490 3545 3591 3593 3640 3647 3673 3678 3707 3740 3816 3826 3831 3878 3906 3920 3939 3954 3970 3984 4056','general')
add('2631 2683 2690 2693 2709 2733 2801 2806 2832 2834 2869 2878 2888 2900 2953 2958 2968 2981 2999 3013 3018 3019 3031 3036 3056 3069 3087 3093 3096 3097 3184 3194 3232 3235 3257 3259 3262 3281 3286 3294 3340 3354 3401 3418 3430 3431 3469 3476 3533 3539 3560 3606 3611 3613 3617 3618 3626 3627 3641 3700 3730 3745 3749 3805 3811 3847 3935 3989 4002 4013 4046 4064 2830 2991 3196 3369 3379 3433 3520 3536 3592 3637 3674 3699 3870 3963 4063','cool')
add('2703 2709 2888 2968 3019 3294 3431 3611 3617 3730 3866 3919 4002 3906 2830 2991 3369 3379 3433 3536 3637 3699 3870 4063','soft')
add('2631 2834 3037 3096 3257 3262 3354 3469 3539 3613 3618 3626 4046','weight')
add('3019 3087 3172 3210 3354 3418 3533 3560 3572 3700 3805 3847 3920 2830 3196 3379 3433 3637 3674 3699','sleep')
add('2683 2981 3257 3866 3939 3637 4063','care')
add('2882 2903 2832 3340 3354','value');add('2902 2968','quality');add('2717 3211 3037 3627','color');add('3281','fit');add('3420','service')
add('2649 2659 2754 2826 2877 2890 2893 2937 3013 3031 3232 3617 3651 3852 3350 3732 3708 3760 3865 3957 3887','', 'quality')
add('2754 2877 3651','', 'care');add('2715 2754 2890 2893 2932 3013 3155 3651 3819 3894','', 'value')
add('2719 3793','', 'slip');add('2734 3031 3430 3745','', 'soft')
add('2751 2778 2834 2981 3284 3728 3428 3717','', 'color')
add('2932 3641 3852','', 'weight');add('3384 3386 3554 3894 3967','', 'fit')
add('3058','', 'odor');add('3516 4057 3865','', 'service');add('3841','', 'contents')
add('2701 3155','', 'general');add('2649 2715 2826 2877 3284 3655 3728 4057','general')
add('2659 2778','cool');add('2778','weight');add('3554','service')
# Source object audit is retained separately, rather than mixing pillowcases into a comforter.
rejected=[]
for i in excluded:
 x=by[i].copy();x['exclusion_reason']='只有数字，没有可分析的体验文字' if i==3159 else ('内容为送风设备，非凉感被' if i==3661 else '正文研究对象为枕头／枕套，非本款凉感被')
 rejected.append(x)
(R/'cozy_excluded.json').write_text(json.dumps(rejected,ensure_ascii=False,indent=2))
(R/'cozy_overrides.json').write_text(json.dumps({str(x['id']):{'positive':x['positive'],'negative':x['negative']} for x in a if x['id'] not in excluded},ensure_ascii=False,indent=2))
(R/'cozy_excluded_ids.json').write_text(json.dumps(excluded))
c=sqlite3.connect(B/'data/library.sqlite3')
for i in excluded:c.execute("DELETE FROM reviews WHERE id=? AND product_id='cozy-comforter'",(i,))
c.commit();c.close()
print('排除',len(excluded),'条；保留',len(a)-len(excluded),'条独立凉感被评论；排除原文保存在cozy_excluded.json')
