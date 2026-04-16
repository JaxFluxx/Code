package enums;
/**
 * This program demonstrates enumerated types by a class.
 * @version 1.0 2018-10-24
 * @author He Yongqiang
 */
public final class Season {
	public int index;
	public String name;
	private Season(int index,String name) {
		this.index=index;
		this.name=name;
	}
	public static final Season SPRING=new Season(1,"春季");
	public static final Season SUMMER=new Season(2,"夏季");
	public static final Season AUTUMN=new Season(3,"秋季");
	public static final Season WINTER=new Season(4,"冬季");
}

class SeasonTest{
	public static void main(String[] args) {
		Season.SPRING.index=5;
		System.out.println(Season.SPRING.index + Season.SPRING.name);
	}
}
