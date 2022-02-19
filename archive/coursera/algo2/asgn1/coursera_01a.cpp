#include <iostream>
#include <algorithm>
using namespace std;
#define pii pair<long long,long long>
bool cmp1(pii p1,pii p2){
    if((p1.first-p1.second) == (p2.first-p2.second)) return p1.first > p2.first;
    return (p1.first-p1.second) > (p2.first-p2.second);
}
bool cmp2(pii p1,pii p2){
    if(((long double)p1.first/p1.second*1.0) == ((long double)p2.first/p2.second*1.0)) return p1.first > p2.first;
    return ((long double)p1.first/p1.second*1.0) > ((long double)p2.first/p2.second*1.0);
}
int main (int argc, char const* argv[])
{
    int tc; cin>>tc;
    pii data[tc];
    for (unsigned int i = 0; i <tc; i += 1)
    {
        cin>>data[i].first>>data[i].second;
    }
    sort(data,data+tc,cmp1);
    long long start_time =0;
    long long total =0;
    for (int i = 0; i < tc; i += 1)
    {
        start_time+=data[i].second;
        total+=(data[i].first*start_time);
    }
    cout<<total<<"\n";
    
    sort(data,data+tc,cmp2);
    start_time =0;
    total =0;
    for (int i = 0; i < tc; i += 1)
    {
        start_time+=data[i].second;
        total+=(data[i].first*start_time);
    }
    cout<<total<<"\n";
    return 0;
}
/*
86094025078
86086706122
*/
